import csv
import argparse
from os import X_OK, makedirs
from shutil import copy
from tools.configuration import DatabaseConfig, parse_config
from pathlib import Path

PATH_INDEX = 5
CONFIG_FILE_PATH = Path("config.cfg")
# This script extract from an exported ammod csv a ballanced dataset,
# smallest amount samples of a class defines amount for all other classes
DATA_FILEPATH = "labels.csv"


def copy_files(
    labels_csv: Path,
    target_path: Path,
    config_path: Path = CONFIG_FILE_PATH,
    path_index: int = PATH_INDEX,
):
    config = parse_config(config_path)
    if labels_csv.exists() == False:
        raise Exception("CSV file does not exists")
    if target_path.exists() == False:
        raise Exception("Target path does not exists")

    with open(labels_csv) as dataFile:
        dataframe = csv.reader(dataFile, delimiter=";", quotechar="|",)
        fieldnames = dataframe.__next__()
        distinct = set()
        for x in dataframe:
            distinct.add(x[path_index])

        for x in distinct:

            filepath = config.database.file_storage_path.joinpath(x)
            target_filepath = target_path.joinpath(x)

            if target_filepath.exists() == False:
                makedirs(target_filepath.parent, exist_ok=True)

                try:
                    copy(filepath, target_filepath)
                except FileNotFoundError as e:
                    print("FileNotFoundError: {}".format(e))


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--dir", metavar="path", type=Path, nargs="?", help="target folder",
)

parser.add_argument(
    "--csv", metavar="path", type=Path, help="csv file with all entries",
)
parser.add_argument(
    "--config",
    metavar="path",
    type=Path,
    nargs="?",
    default=CONFIG_FILE_PATH,
    help="config file with database credentials",
)

parser.add_argument(
    "--index",
    metavar="path",
    type=int,
    nargs="?",
    default=PATH_INDEX,
    help="column index in csv of filepath",
)

args = parser.parse_args()
if __name__ == "__main__":
    copy_files(args.csv, args.dir, config_path=args.config, path_index=args.index)
