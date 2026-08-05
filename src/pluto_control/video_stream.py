import argparse
import socket
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class StreamConfig:
    host: str = "0.0.0.0"
    port: int = 5600
    frame_timeout_sec: float = 2.0


class PlutoVideoStreamReceiver:
    def __init__(self, config: StreamConfig) -> None:
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.config.host, self.config.port))
        self.sock.settimeout(self.config.frame_timeout_sec)

    def receive_and_display(self) -> None:
        print(
            f"Listening for Pluto video stream on {self.config.host}:{self.config.port}..."
        )
        print("Press 'q' in the video window to stop.")

        while True:
            try:
                data, _ = self.sock.recvfrom(65535)
            except socket.timeout:
                continue

            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                continue

            cv2.imshow("Pluto Camera Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.close()

    def close(self) -> None:
        self.sock.close()
        cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Receive and display UDP MJPEG-like stream from Pluto drone extension"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=5600, help="UDP port to bind")
    parser.add_argument(
        "--timeout", type=float, default=2.0, help="Socket timeout in seconds"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = StreamConfig(host=args.host, port=args.port, frame_timeout_sec=args.timeout)
    receiver = PlutoVideoStreamReceiver(config)
    try:
        receiver.receive_and_display()
    finally:
        receiver.close()


if __name__ == "__main__":
    main()
