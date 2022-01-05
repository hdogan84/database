from typing import NamedTuple, List
from pathlib import Path
from tools.errors import NoAnnoationFileError, ToManyAnnoationFilesError
from shutil import copy

CorespondingFiles = NamedTuple(
    "CorespondingFiles",
    [
        ("audio_file", Path),
        ("annoation_file", Path),
    ],
)


def get_record_annoation_tupels_from_directory(
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
            f
            for f in annoation_files
            if (
                f.stem.startswith(audio_file.stem)
                and not f.stem.startswith(audio_file.stem + "_S")
            )
        ]
        if len(matching_annotation_files) > 1:
            # raise ToManyAnnoationFilesError(audio_file, matching_annotation_files)
            print(
                "To many Annoation files found for {}: {}".format(
                    audio_file, matching_annotation_files
                )
            )
            continue
        if len(matching_annotation_files) == 0:
            # raise NoAnnoationFileError(audio_file)
            print("No Annoation file found for {}.".format(audio_file))
            continue
        coresponding_files.append((audio_file, matching_annotation_files[0]))
    # adding data_path to files name
    result = list(
        map(
            lambda rf: CorespondingFiles(audio_file=rf[0], annoation_file=rf[1]),
            coresponding_files,
        )
    )
    return result


def rename_and_copy_to(file_path: Path, target_folder: Path, target_name: str):
    target_file_path = target_folder.joinpath("{}".format(target_name))
    copy(file_path, target_file_path)
