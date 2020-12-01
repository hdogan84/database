from mysql.connector.cursor import MySQLCursor
from pathlib import Path
import errno
import os
import shutil
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
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor
            db_cursor.execute(
                """
            SELECT 
                id, filename, md5sum
            FROM
                record
            """
            )
            print("Start creating subfolders")
            for record in db_cursor.fetchall():
                file_path = "{}/{}/{}/".format(record[2][0], record[2][1], record[2][2])
                target_folder.joinpath(file_path).mkdir(parents=True, exist_ok=True)
                db_cursor.execute(
                    """
                UPDATE record SET file_path =%s WHERE id=%s
                """,
                    (file_path, record[0]),
                )
            db_connection.commit()
            print("Finished creating subfolders and adding to database")
            print("Start moving files ")
            db_cursor.execute(
                """
            SELECT 
                id,  file_path, filename
            FROM
                record
            """
            )
            for record in db_cursor.fetchall():
                src = config.database.file_storage_path.joinpath("original", record[2])
                target = target_folder.joinpath(record[1], record[2])
                shutil.move(src, target)


if __name__ == "__main__":
    fix_file_path(TARGET_FILE_PATH)
    pass
