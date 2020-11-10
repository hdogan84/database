from typing import NamedTuple
from pathlib import Path
from uuid import uuid4
from mimetypes import guess_type
from hashlib import md5

import wave
from pydub.utils import mediainfo


AudioFileParameters = NamedTuple(
    "AudioFileParameters",
    [
        ("sample_rate", int),
        ("bit_depth", int),
        ("bit_rate", int),
        ("duration", float),
        ("channels", int),
        ("mime_type", str),
        ("original_file_name", str),
        ("file_name", str),
        ("md5sum", str),
    ],
)

# 'sample_rate':'48000'
# 'channels':'2'
# 'channel_layout':'unknown'
# 'bits_per_sample':'16'

# 'duration':'300.000000'
def read_parameters_from_audio_file(file: Path) -> AudioFileParameters:
    original_file_name = file.name
    file_name = uuid4().hex + file.suffix
    mime_type = guess_type(file.name)[0]
    md5sum = md5(open(file, "rb").read()).hexdigest()

    media_info = mediainfo(file)

    return AudioFileParameters(
        original_file_name=original_file_name,
        file_name=file_name,
        mime_type=mime_type,
        md5sum=md5sum,
        sample_rate=int(media_info["sample_rate"]),
        bit_depth=None
        if int(media_info["bits_per_sample"]) is 0
        else int(media_info["bits_per_sample"]),
        bit_rate=int(media_info["bit_rate"]),
        channels=int(media_info["channels"]),
        duration=float(media_info["duration"]),
    )
