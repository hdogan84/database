from typing import List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
from import_scripts.import_annoations_olaf import ANNOTATION_STRATEGY
from tools.logging import debug, progbar
from tools.configuration import DatabaseConfig, parse_config
from tools.db import connectToDB
from derivates import Standart32khz
import argparse
from tools.file_handling.csv import write_to_csv
from enum import Enum, IntEnum
from export_scripts.export_tools import map_filename_to_derivative_filepath
import librosa
import warnings
from tools.db import update_entry
from tools.file_handling.csv import write_to_csv

warnings.filterwarnings("ignore")
CONFIG_FILE_PATH = Path("config_training.cfg")

query_files = """
SELECT 
   r.id, r.file_path, r.filename, r.duration, r.sample_rate
FROM
    record AS r 

"""
ROOT = Path("/home/tsa/projects/libro-animalis/data/original")


class Index(IntEnum):
    ID = 0
    FILE_PATH = 1
    FILENAME = 2
    DURATION = 3
    SAMPLE_RATE = 4


def check_files(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_files)
            data = db_cursor.fetchall()
            total = len(data)
            print("Found {} records".format(len(data)))
            counter = 0
            broken_list = ["asdasdas"]
            lastrun = 555244 * 0.32709
            for index, record in enumerate(data):
                filepath = ROOT.joinpath(record[Index.FILE_PATH]).joinpath(
                    record[Index.FILENAME]
                )
                if index < lastrun:
                    continue
                try:
                    y, sr = librosa.load(filepath, sr=None)
                    duration = librosa.get_duration(y, sr=sr)
                    if duration != record[Index.DURATION]:
                        # print(
                        #     " {}: {} != {}".format(
                        #         record[Index.ID], duration, record[Index.DURATION]
                        #     )
                        # )
                        counter = counter + 1
                        update_entry(
                            db_cursor,
                            "record",
                            [("duration", duration), ("sample_rate", sr)],
                            [("id", record[Index.ID])],
                        )
                        db_connection.commit()
                except Exception:
                    broken_list.append(filepath.as_posix())
                    write_to_csv(broken_list, "broken_files.csv", ["path"])

                progbar(index, total, 20, end=" fixed: {}/{}".format(counter, total))

            #     print(record[Index.DURATION])
            write_to_csv(broken_list, "broken_files.csv", ["path"])


def export_data(
    config_path: Path = CONFIG_FILE_PATH,
):
    config = parse_config(config_path)

    print("Check file durations")
    check_files(config)


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
    export_data(
        config_path=args.config,
    )
