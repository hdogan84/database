from uuid import uuid4
from pathlib import Path
from typing import List, NamedTuple
from datetime import date, time, datetime
from mimetypes import guess_type
from hashlib import md5
import wave
from tools.errors import NoAnnoationFileError, ToManyAnnoationFilesError

CorespondingFiles = NamedTuple(
    "CorespondingFiles",
    [
        ("audio_file", Path),
        ("annoation_file", Path),
    ],
)


def get_record_annoation_tupels(
    data_path: Path,
    record_file_ending: str = ".wav",
    annoation_file_ending: str = ".csv",
) -> List[CorespondingFiles]:
    all_files = [f for f in data_path.iterdir() if f.is_file()]
    audio_files = [Path(f) for f in all_files if f.suffix == record_file_ending]
    annoation_files = [
        Path(f) for f in all_files if (f.suffix == annoation_file_ending)
    ]

    coresponding_files = list()

    for audio_file in audio_files:
        matching_annotation_files = [
            f for f in annoation_files if (f.stem.startswith(audio_file.stem))
        ]
        if len(matching_annotation_files) > 1:
            raise ToManyAnnoationFilesError(audio_file, matching_annotation_files)
        if len(matching_annotation_files) == 0:
            raise NoAnnoationFileError(audio_file)
        coresponding_files.append((audio_file, matching_annotation_files[0]))
    # adding data_path to files name
    result = list(
        map(
            lambda rf: CorespondingFiles(
                audio_file=rf[0], annoation_file=data_path / rf[1]
            ),
            coresponding_files,
        )
    )
    return result


FileNameInformations = NamedTuple(
    "FileNameInformations_name_date_time",
    [
        ("location_name", str),
        ("record_date", date),
        ("record_time", time),
    ],
)


def parse_file_name_location_date_time(file_name: str) -> FileNameInformations:
    parts = file_name.split(sep="_", maxsplit=1)
    location_name = parts[0]
    record_datetime = datetime.strptime(parts[1], "%Y%m%d_%H%M%S")
    return FileNameInformations(
        location_name=location_name,
        record_date=record_datetime.date(),
        record_time=record_datetime.time(),
    )


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
