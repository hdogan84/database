import csv
import pandas
from pathlib import Path
from typing import Dict, List
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from tools.file_handling.collect import rename_and_copy_to
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config
from tools.logging import debug, info, error
from tools.db.queries import get_id_of_entry_in_table
from tools.db import (
    get_entry_id_or_create_it,
    connectToDB,
    delete_from_table,
)

import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")

from tools.logging import info, progbar
import argparse

TARGET_DATA_PATH = "./tmp"
CONFIG_FILEPATH = "/home/tsa/projects/libro-animalis/src/config/config_crawled.cfg"
DATA_PATH = "/home/tsa/projects/libro-animalis/downloads/xeno_canto-ammod"
CSV_FILEPATH = (
    "/home/tsa/projects/libro-animalis/downloads/xeno_canto-ammod/collection-data.csv"
)
COLLECTION_NAME = "xeno canta 2020-2021 ammod set"
DRY_RUN = False
# recordist;location_name;latitude;longitude;altitude;original_filename;xeno_canto_id;call_type;date;time;species;background
def import_collection(
    data_path, config_path, csv_filepath, collection_name, dry_run=True
):
    config = parse_config(config_path)
    print(config_path)
    dataframe = pandas.read_csv(csv_filepath, sep=";", quotechar="|", index_col=False)

    print(config.database.host)
    print(config.database.port)
    print(config.database.user)
    print(config.database.password)
    print(config.database.name)
    info("Start importing files")
    with connectToDB(config.database) as db_connection:
        print("Connected")
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor

            collection_entry = [("name", collection_name), ("remarks", None)]
            collection_id = get_entry_id_or_create_it(
                db_cursor, "collection", collection_entry, collection_entry
            )
            counter = 0
            failed_annotations = []
            row_count = dataframe.shape[0]
            for _, row in dataframe.iterrows():
                progbar(counter, row_count, 20)
                counter = counter + 1
                if counter % 1000 == 0:
                    if dry_run is False:
                        db_connection.commit()

                species_id = None

                filepath = data_path.joinpath(str(row.loc["original_filename"]))

                if filepath.exists() is False:
                    error("File does not exist {}".format(filepath.as_posix()))
                    continue
                audio_file_parameters = None
                try:
                    audio_file_parameters = read_parameters_from_audio_file(filepath)
                except Exception as e:
                    error("Could not read audio Parameters from {}".format(filepath))
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
                    (
                        "original_filename",
                        audio_file_parameters.original_filename,
                    ),
                    ("file_path", target_record_file_path),
                    ("filename", audio_file_parameters.filename),
                    ("md5sum", audio_file_parameters.md5sum),
                    ("collection_id", collection_id),
                ]

                (record_id, created) = get_entry_id_or_create_it(
                    db_cursor,
                    "record",
                    [
                        ("md5sum", audio_file_parameters.md5sum),
                    ],
                    data=record_entry,
                    info=True,
                )
                if created:
                    # move file to destination
                    if dry_run is False:
                        targetDirectory = (
                            config.database.get_originals_files_path().joinpath(
                                target_record_file_path
                            )
                        )
                        targetDirectory.mkdir(parents=True, exist_ok=True)
                        rename_and_copy_to(
                            filepath,
                            targetDirectory,
                            audio_file_parameters.filename,
                        )

                species_id = get_id_of_entry_in_table(
                    db_cursor, "species", [("latin_name", row.loc["species"])]
                )

                if species_id is None:
                    failed_annotations.append(
                        (row.loc["species"], audio_file_parameters.original_filename)
                    )
                    print("failed _annoation species id not found")
                    continue
                # create foreground annoation
                annoation_data = [
                    ("record_id", record_id),
                    ("start_time", 0),
                    ("end_time", audio_file_parameters.duration),
                    ("species_id", species_id),
                    ("background", bool(row.loc["background"])),
                ]
                get_entry_id_or_create_it(
                    db_cursor,
                    "annotation_of_species",
                    query=annoation_data,
                    data=annoation_data,
                )
                if dry_run is False:
                    db_connection.commit()

            print(failed_annotations)


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
    default=CSV_FILEPATH,
)
parser.add_argument(
    "--config",
    metavar="path",
    type=Path,
    nargs="?",
    default=CONFIG_FILEPATH,
    help="config file with database credentials",
)

parser.add_argument(
    "--collection",
    metavar="path",
    type=str,
    nargs="?",
    default=COLLECTION_NAME,
    help="config file with database credentials",
)

args = parser.parse_args()
if __name__ == "__main__":
    import_collection(
        args.data_path, args.config, args.csv_path, args.collection, dry_run=DRY_RUN
    )
