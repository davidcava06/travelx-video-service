from google.cloud.video import transcoder_v1
from google.protobuf import duration_pb2 as duration


def create_video_stream(
    key: str, height: int, width: int, bitrate: int, frame_rate: float
) -> transcoder_v1.types.ElementaryStream:
    return transcoder_v1.types.ElementaryStream(
        key=f"video-{key}",
        video_stream=transcoder_v1.types.VideoStream(
            h264=transcoder_v1.types.VideoStream.H264CodecSettings(
                height_pixels=height,
                width_pixels=width,
                bitrate_bps=bitrate,
                frame_rate=frame_rate,
            ),
        ),
    )


def create_audio_stream(
    key: str, codec: str, bitrate: int
) -> transcoder_v1.types.ElementaryStream:
    return transcoder_v1.types.ElementaryStream(
        key=f"audio-{key}",
        audio_stream=transcoder_v1.types.AudioStream(codec=codec, bitrate_bps=bitrate),
    )


def create_mux_stream(key: str, streams: list) -> transcoder_v1.types.MuxStream:
    return transcoder_v1.types.MuxStream(
        key=key,
        container="ts",
        elementary_streams=streams,
        segment_settings=transcoder_v1.types.SegmentSettings(
            individual_segments=True,
        )
    )


def create_manifest(mux_streams: list) -> transcoder_v1.types.Manifest:
    return transcoder_v1.types.Manifest(
        type_="HLS",
        mux_streams=mux_streams,
    )


elementary_streams = [
    create_video_stream(
        key="sd", height=842, width=480, bitrate=1400000, frame_rate=60
    ),
    create_audio_stream(key="sd", bitrate=128000, codec="aac"),
    create_video_stream(
        key="hd", height=1280, width=720, bitrate=280000, frame_rate=60
    ),
    create_audio_stream(key="hd", bitrate=128000, codec="aac"),
]
mux_streams = [
    create_mux_stream(key="sd", streams=["video-sd", "audio-sd"]),
    create_mux_stream(key="hd", streams=["video-hd", "audio-hd"]),
]
manifest = create_manifest(["sd", "hd"])


def create_standard_job_config(thumbnail_uri: str) -> transcoder_v1.types.JobConfig:
    return transcoder_v1.types.JobConfig(
        elementary_streams=elementary_streams,
        mux_streams=mux_streams,
        manifests=[manifest],
    )
