from typing import Collection, List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
from tools.logging import debug
from tools.configuration import DatabaseConfig, parse_config
from tools.db import connectToDB
from tools.file_handling.csv import write_to_csv
from derivates import Standart32khz
import argparse


CONFIG_FILE_PATH = Path("config.cfg")

collections = [
    "dcase-2018-freefield1010",
    "dcase-2018-warblrb10k",
    "dcase-2018-BirdVox-DCASE-20k.csv",
]

query_files = """
SELECT 
    distinct(r.filename), r.file_path
FROM
    annotation_of_noise AS a
        LEFT JOIN
    record AS r ON r.id = a.record_id
    LEFT JOIN
    collection AS c ON c.id = r.collection_id
WHERE c.`name` = %s
ORDER BY RAND()
    LIMIT 1000;

"""


def create_file_derivates(config: DatabaseConfig) :
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            file_list = []
            for collection in collections:
                db_cursor.execute(query_files, [collection])
                data = db_cursor.fetchall()
                file_list.extend(data)
            filepathes = list(map(lambda x: (Path(x[1]).joinpath(x[0])), file_list))
            derivatateCreator = Standart32khz(config.database)
            file_derivates_dict = derivatateCreator.get_original_derivate_dict(
                filepathes
            )
            return file_derivates_dict


def cut_path_to_essential(filepath: Path) -> str:
    essential = Path("").joinpath(*filepath.parts[len(filepath.parts) - 6 :])
    return essential.as_posix()


def export_data(config_path: Path = CONFIG_FILE_PATH,csv_filename="noise.csv"):
    config = parse_config(config_path)
    derivates_dict = create_file_derivates(config)
    data = [[cut_path_to_essential(x)] for x in derivates_dict.values()]
    write_to_csv(data, csv_filename, ["filepath"])


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--csv_filename",
    metavar="string",
    type=str,
    nargs="?",
    default="labels.csv",
    help="target filename for label csv",
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
    export_data(
        config_path=args.config, csv_filename=args.csv_filename,
    )
