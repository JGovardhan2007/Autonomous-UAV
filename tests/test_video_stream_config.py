from src.pluto_control.video_stream import StreamConfig


def test_stream_config_defaults() -> None:
    config = StreamConfig()
    assert config.host == "0.0.0.0"
    assert config.port == 5600
    assert config.frame_timeout_sec == 2.0
