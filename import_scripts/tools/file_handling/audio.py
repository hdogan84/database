from typing import NamedTuple
from pathlib import Path
from uuid import uuid4
from mimetypes import guess_type
from hashlib import md5
import wave


AudioFileParameters = NamedTuple(
    "AudioFileParameters",
    [
        ("sample_rate", int),
        ("bit_depth", int),
        ("duration", int),
        ("channels", int),
        ("mime_type", str),
        ("original_file_name", str),
        ("file_name", str),
        ("md5sum", str),
    ],
)


def read_parameters_from_audio_file(file: Path) -> AudioFileParameters:
    original_file_name = file.name
    file_name = uuid4().hex + file.suffix
    mime_type = guess_type(file.name)[0]
    md5sum = md5(open(file, "rb").read()).hexdigest()
    with wave.open(open(file, "rb"), mode="rb") as wave_fp:
        params = wave_fp.getparams()
        return AudioFileParameters(
            original_file_name=original_file_name,
            file_name=file_name,
            mime_type=mime_type,
            md5sum=md5sum,
            sample_rate=params.framerate,
            bit_depth=params.sampwidth * 8,
            channels=params.nchannels,
            duration=params.nframes / params.framerate,
        )
