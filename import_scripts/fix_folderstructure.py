from mysql.connector.cursor import MySQLCursor
from pathlib import Path
import errno
import os
from tools.configuration import parse_config
from tools.db import (
    connectToDB,
    get_entries_from_table,
    update_entry,
    get_synonyms_dict,
)
from tools.configuration import parse_config
from tools.db.queries import get_synonyms_dict
from tools.logging import debug, info

CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")
TARGET_FILE_PATH = Path("libro_animalis/data/original_v2")


def fix_file_path(target_folder: Path, config: Path = CONFIG_FILE_PATH):
    config = parse_config(config)
    if target_folder.exists() is False:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), target_folder)
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:MySQLCursor:
            db_cursor: MySQLCursor
            for entry in os.scandir(config.database.file_storage_path.joinpath("original")):
                if entry.is_dir():
                    continue
                print(entry.name)


if __name__ == "__main__":
    fix_file_path(TARGET_FILE_PATH)
    pass