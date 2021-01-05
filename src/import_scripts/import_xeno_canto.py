from os import name
from typing import NamedTuple, List
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from urllib.request import urlopen
from xmltodict import parse
from tools.logging import debug, info, error
import csv
import argparse
from math import ceil
from pathlib import Path
from tools.configuration import parse_config
from tools.file_handling.audio import read_parameters_from_audio_file
from datetime import date, datetime
from tools.db import sanitize_name, sanitize_altitude
from tools.db.table_types import XenoCantoRow

from tools.file_handling.collect import rename_and_copy_to

from tools.db import (
    connectToDB,
    get_entry_id_or_create_it,
    get_id_of_entry_in_table,
    get_synonyms_dict,
)

CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")
CSV_FILEPATH = Path("libro_animalis/data/birdsounds.csv")
FILES_DIRECTORY_PATH = Path(
    "/home/bewr/external-volumes/stana/mnt/z/AG/TSA/Mario/_Backups/XenoCantoDisk/sounds/"
)


def import_dase_noise(
    files_path=FILES_DIRECTORY_PATH,
    config_path=CONFIG_FILE_PATH,
    csv_filepath=CSV_FILEPATH,
    collection_name: str = None,
    file_ending="wav",
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
                        db_connection.commit()

                    #
                    species_id = None
                    filepath = files_path.joinpath("{}.{}".format(row[0], file_ending))

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
                        targetDirectory = config.database.get_originals_files_path().joinpath(
                            target_record_file_path
                        )
                        targetDirectory.mkdir(parents=True, exist_ok=True)
                        rename_and_copy_to(
                            filepath, targetDirectory, audio_file_parameters.filename,
                        )
                    # create foreground annoation
                    forground_annoation = [
                        ("record_id", record_id),
                        ("species_id", species_id),
                        ("background", False),
                        ("individual_id", None),
                        ("group_id", None),
                        ("vocalization_type", xeno.songtype),
                        ("quality_tag", None),
                        ("start_time", 0),
                        ("end_time", audio_file_parameters.duration),
                        ("start_frequency", None),
                        ("end_frequency", None),
                        ("channel", None),
                        ("annotator_id", person_id),
                    ]
                    # print(forground_annoation)
                    get_entry_id_or_create_it(
                        db_cursor,
                        "annotation_of_species",
                        forground_annoation,
                        forground_annoation,
                    )

                    background_species = xeno.background.split(",")
                    for species in background_species:
                        back_species_id = get_species_id(latin_name, xeno.eng_name)
                        if back_species_id is None:
                            missed_imports.append(row)
                            error(
                                "Could not identify species{}, {} ".format(
                                    latin_name, xeno.eng_name
                                )
                            )
                            continue
                        background_annoation = [
                            ("record_id", record_id),
                            ("species_id", species_id),
                            ("background", True),
                            ("individual_id", None),
                            ("group_id", None),
                            ("vocalization_type", None),
                            ("quality_tag", None),
                            ("start_time", 0),
                            ("end_time", audio_file_parameters.duration),
                            ("start_frequency", None),
                            ("end_frequency", None),
                            ("channel", None),
                            ("annotator_id", person_id),
                        ]
                        get_entry_id_or_create_it(
                            db_cursor,
                            "annotation_of_species",
                            background_annoation,
                            background_annoation,
                        )
                db_connection.commit()


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--files",
    metavar="path",
    type=Path,
    nargs="?",
    help="target folder",
    default=FILES_DIRECTORY_PATH,
)

parser.add_argument(
    "--csv",
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
    default=CONFIG_FILE_PATH,
    help="config file with database credentials",
)

args = parser.parse_args()
if __name__ == "__main__":
    import_xeno_canto(files=args.files, config_path=args.config, csv_path=args.csv)