from os import listdir
from os.path import isfile, join, splitext
from typing import List, Tuple
from tools.errors import NoAnnoationFileError, ToManyAnnoationFilesError


def get_record_annoation_tupels(
    data_path: str,
    record_file_ending: str = ".wav",
    annoation_file_ending: str = ".txt",
) -> List[Tuple[str, str]]:
    all_files = [f for f in listdir(data_path) if (isfile(join(data_path, f)))]

    audio_files = [f for f in all_files if (splitext(f)[1] == record_file_ending)]
    annoation_files = [
        f for f in all_files if (splitext(f)[1] == annoation_file_ending)
    ]

    coresponding_files = list()

    for audio_file in audio_files:
        matching_annotation_files = [
            f
            for f in annoation_files
            if (splitext(f)[0].startswith(splitext(audio_file)[0]))
        ]
        if len(matching_annotation_files) > 1:
            raise ToManyAnnoationFilesError(audio_file, matching_annotation_files)
        if len(matching_annotation_files) == 0:
            raise NoAnnoationFileError(audio_file)
        coresponding_files.append((audio_file, matching_annotation_files[0]))
    # adding data_path to files name
    result = list(
        map(
            lambda rf: (join(data_path, rf[0]), join(data_path, rf[1])),
            coresponding_files,
        )
    )
    return result
