# Autonomous-UAV

## Pluto Control (Drona Aviation) Video Stream

This project now includes an initial Pluto video stream receiver.

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r /home/runner/work/Autonomous-UAV/Autonomous-UAV/requirements.txt
```

### Run the stream receiver

```bash
python /home/runner/work/Autonomous-UAV/Autonomous-UAV/src/pluto_control/video_stream.py --host 0.0.0.0 --port 5600
```

It listens for UDP image frames and displays them in an OpenCV window.
Press `q` to quit.
