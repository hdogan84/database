import csv
from pathlib import Path
from typing import Dict, List
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from tools.file_handling.collect import rename_and_copy_to
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config
from tools.logging import debug, info, error
from tools.db import (
    get_entry_id_or_create_it,
    connectToDB,
)
from tools.logging import info
import argparse

DATA_PATH = Path(
    "/mnt/tsa_transfer/TrainData/BAD_Challenge_18/DatasetsOrgDownloads/Development"
)
CONFIG_FILEPATH = Path("./config.cfg")
CSV_PATH = Path("./assets/dcase-2018")
# CSV_FILES = ["freefield1010.csv"]
# CSV_FILES = ["warblrb10k.csv"]
CSV_FILES = ["BirdVox-DCASE-20k.csv"]

# DIRS = ["ff1010bird/wav"]
# DIRS = ["warblrb10k_public/wav"]
DIRS = ["BirdVoxDCASE20k/wav"]

# COLLECTIONS = ["dcase-2018-freefield1010"]
# COLLECTIONS = ["dcase-2018-warblrb10k"]
COLLECTIONS = ["dcase-2018-BirdVox-DCASE-20k.csv"]
# ,
# "dcase-2018-warblrb10k",
# "dcase-2018-BirdVox-DCASE-20k.csv",
# ]


def import_noise(
    data_path,
    config_path,
    csv_filepath,
    collection_name: str = None,
    file_ending="wav",
    dry_run=True,
):
    config = parse_config(config_path)

    with open(csv_filepath, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        # remove header
        next(csv_reader)

        with connectToDB(config.database) as db_connection:
            with db_connection.cursor() as db_cursor:
                db_cursor: MySQLCursor

                collection_entry = [("name", collection_name), ("remarks", None)]
                collection_id = get_entry_id_or_create_it(
                    db_cursor, "collection", collection_entry, collection_entry
                )
                counter = 0
                for row in csv_reader:
                    if row[2] == 1:
                        # filter bird signals
                        continue
                    counter = counter + 1
                    if counter % 1000 == 0:
                        if dry_run is False:
                            db_connection.commit()

                    #
                    species_id = None
                    filepath = data_path.joinpath("{}.{}".format(row[0], file_ending))

                    if filepath.exists() is False:
                        error("File does not exhist {}".format(filepath.as_posix()))
                        continue
                    audio_file_parameters = None
                    try:
                        audio_file_parameters = read_parameters_from_audio_file(
                            filepath
                        )
                    except:
                        error(
                            "Could not read audio Parameters from {}".format(filepath)
                        )
                        continue

                    target_record_file_path = "{}/{}/{}".format(
                        audio_file_parameters.md5sum[0],
                        audio_file_parameters.md5sum[1],
                        audio_file_parameters.md5sum[2],
                    )
                    record_entry = [
                        ("duration", audio_file_parameters.duration),
                        ("sample_rate", audio_file_parameters.sample_rate),
                        ("bit_depth", audio_file_parameters.bit_depth),
                        ("bit_rate", audio_file_parameters.bit_rate),
                        ("channels", audio_file_parameters.channels),
                        ("mime_type", audio_file_parameters.mime_type),
                        ("original_filename", audio_file_parameters.original_filename,),
                        ("file_path", target_record_file_path),
                        ("filename", audio_file_parameters.filename),
                        ("md5sum", audio_file_parameters.md5sum),
                        ("collection_id", collection_id),
                    ]

                    (record_id, created) = get_entry_id_or_create_it(
                        db_cursor,
                        "record",
                        [("md5sum", audio_file_parameters.md5sum),],
                        data=record_entry,
                        info=True,
                    )
                    if created:
                        # move file to destination
                        if dry_run is False:
                            targetDirectory = config.database.get_originals_files_path().joinpath(
                                target_record_file_path
                            )
                            targetDirectory.mkdir(parents=True, exist_ok=True)
                            rename_and_copy_to(
                                filepath,
                                targetDirectory,
                                audio_file_parameters.filename,
                            )
                    # create foreground annoation
                    forground_annoation = [
                        ("record_id", record_id),
                        ("start_time", 0),
                        ("end_time", audio_file_parameters.duration),
                        ("start_frequency", None),
                        ("end_frequency", None),
                        ("channel", None),
                        ("annotator_id", None),
                    ]
                    # print(forground_annoation)
                    get_entry_id_or_create_it(
                        db_cursor,
                        "annotation_of_noise",
                        forground_annoation,
                        forground_annoation,
                    )
                    if dry_run is False:
                        db_connection.commit()
                    print(filepath)


def import_dcase_noise(data_path: Path, csv_path: Path, config_filepath: Path):
    for collection, csv_file, dir in zip(COLLECTIONS, CSV_FILES, DIRS):
        import_noise(
            data_path.joinpath(dir),
            config_filepath,
            csv_path.joinpath(csv_file),
            collection_name=collection,
            dry_run=False,
        )


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--data_path",
    metavar="path",
    type=Path,
    nargs="?",
    help="target folder",
    default=DATA_PATH,
)


parser.add_argument(
    "--csv_path",
    metavar="path",
    type=Path,
    nargs="?",
    help="csv file with all entries",
    default=CSV_PATH,
)
parser.add_argument(
    "--config",
    metavar="path",
    type=Path,
    nargs="?",
    default=CONFIG_FILEPATH,
    help="config file with database credentials",
)

args = parser.parse_args()
if __name__ == "__main__":
    import_dcase_noise(args.data_path, args.config, args.csv_path)