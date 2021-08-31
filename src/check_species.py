from pathlib import Path
from typing import Dict, List
from math import ceil
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from tools.db.queries import get_id_of_entry_in_table
from tools.file_handling.collect import (
    get_record_annoation_tupels_from_directory,
    rename_and_copy_to,
)
from tools.file_handling.name import parse_filename_for_location_date_time
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config
from tools.sub_scripts.record_information import check_get_ids_from_record_informations
from tools.file_handling.annotation import read_raven_file
from tools.db import (
    get_entry_id_or_create_it,
    connectToDB,
    delete_from_table,
)
from tools.logging import info
import argparse
import pandas

CONFIG_FILE_PATH = Path("../config_training.cfg")
annotation_interval = "annotation_interval"

RECORD_MERGE_STRATEGY = "merge"
ANNOTATION_STRATEGY = "merge"
ANNOTATION_TABLE = "species"
LICENSE = None


def check_data(config_file_path=None):
    config = parse_config(config_file_path)

    # check if all filenames are valid
    df = pandas.read_csv("../marios_bird-256-species.csv", delimiter=";")
    info("Start checkin species files")
    with connectToDB(config.database) as db_connection:

        # start import files
        with db_connection.cursor() as db_cursor:
            for row in df.itertuples():
                species_id = get_id_of_entry_in_table(
                    db_cursor, "species", [("latin_name", row.latin_name)]
                )
                if species_id is None:
                    print("" + row.latin_name + "," + row.german_name)


parser = argparse.ArgumentParser(description="")

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
    check_data(args.config)
