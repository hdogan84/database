from pathlib import Path
from typing import List, Tuple
from tools.errors import NoAnnoationFileError, ToManyAnnoationFilesError


def get_record_annoation_tupels(
    data_path: Path,
    record_file_ending: str = "wav",
    annoation_file_ending: str = "csv",
) -> List[Tuple[str, str]]:
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
            lambda rf: (data_path / rf[0], data_path / rf[1]),
            coresponding_files,
        )
    )
    return result
