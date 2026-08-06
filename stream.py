"""
Pluto Drone - Live Camera Stream Viewer
----------------------------------------
1. pluto.cam() + pluto.connect() opens the only available socket (192.168.0.1:9060)
2. The drone sends raw H264 bytes over that socket
3. We stop plutocontrol from using the socket and pipe the raw bytes
   through ffmpeg ourselves so OpenCV can decode and display frames.

Press q to quit.
"""

import time
import threading
import subprocess
import numpy as np
import cv2
from plutocontrol import Pluto

FRAME_WIDTH  = 640
FRAME_HEIGHT = 480


def main():
    # --- Step 1: Connect using pluto.cam() to reach 192.168.0.1:9060 ---
    print("Connecting to drone camera port (192.168.0.1:9060)...")
    pluto = Pluto()
    pluto.cam()       # sets IP=192.168.0.1, PORT=9060
    pluto.connect()

    if not pluto.connected:
        print("[ERROR] Could not connect. Make sure you are on Pluto WiFi.")
        return

    print("[OK] Connected. Stopping pluto MSP thread to free the socket for video...")

    # --- Step 2: Stop pluto write_function so it stops consuming the socket ---
    pluto._stop_event.set()
    if pluto.thread and pluto.thread.is_alive():
        pluto.thread.join(timeout=2.0)

    raw_socket = pluto.client   # grab the raw socket

    # --- Step 3: Pipe raw socket bytes -> ffmpeg -> decoded BGR frames ---
    ffmpeg_cmd = [
        "ffmpeg",
        "-loglevel", "quiet",
        "-f", "h264",           # tell ffmpeg the stream is raw H.264
        "-i", "pipe:0",         # read from stdin
        "-f", "rawvideo",       # output raw video
        "-pix_fmt", "bgr24",    # OpenCV-compatible pixel format
        "-vf", f"scale={FRAME_WIDTH}:{FRAME_HEIGHT}",
        "pipe:1"                # write to stdout
    ]

    ffmpeg = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    # Thread: pump raw socket data into ffmpeg stdin
    def pump():
        try:
            while True:
                data = raw_socket.recv(65536)
                if not data:
                    break
                ffmpeg.stdin.write(data)
                ffmpeg.stdin.flush()
        except Exception:
            pass
        finally:
            try:
                ffmpeg.stdin.close()
            except Exception:
                pass

    pump_thread = threading.Thread(target=pump, daemon=True)
    pump_thread.start()

    print("[OK] Streaming. Press q in the window to quit.")

    frame_size = FRAME_WIDTH * FRAME_HEIGHT * 3

    try:
        while True:
            raw = ffmpeg.stdout.read(frame_size)
            if len(raw) < frame_size:
                print("[INFO] Stream ended.")
                break

            frame = np.frombuffer(raw, dtype=np.uint8).reshape(
                (FRAME_HEIGHT, FRAME_WIDTH, 3)
            )
            cv2.imshow("Pluto Drone - Live Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[INFO] Quit by user.")
                break
    finally:
        ffmpeg.terminate()
        raw_socket.close()
        cv2.destroyAllWindows()
        print("Stream closed.")


if __name__ == "__main__":
    main()
