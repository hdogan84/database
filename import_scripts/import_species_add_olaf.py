from mysql.connector.cursor import MySQLCursor
from pathlib import Path
import pandas as pd
from tools.configuration import parse_config
from tools.db import (
    connectToDB,
    get_entries_from_table,
    update_entry,
    get_synonyms_dict,
)
from tools.db.queries import get_synonyms_dict
from tools.logging import debug, info

XLSX_FILE_PATH = "database/AMMOD_AV_20201023_CNN_Training_v4.xlsx"
CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

config = parse_config(CONFIG_FILE_PATH)
DF = pd.read_excel(XLSX_FILE_PATH)
selection = DF[
    ["8LetterCode_IOC10.1_New", "GermanName_DOG2019", "ScientificName_DOG2019"]
]
not_matched = []
with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        db_cursor: MySQLCursor
        synonyms_dict = get_synonyms_dict(db_cursor, "do-g_to_ioc10.1")
        for index, row in selection.iterrows():
            result = update_entry(
                db_cursor,
                "species",
                [("german_name", row[1]), ("olaf8_id", row[0])],
                [("latin_name", row[2])],
            )
            if db_cursor.rowcount is 0:
                species_id = synonyms_dict.get(row[2])
                if species_id is not None:
                    result = update_entry(
                        db_cursor,
                        "species",
                        [("german_name", row[1]), ("olaf8_id", row[0])],
                        [("id", species_id)],
                    )

                    if db_cursor.rowcount is 0:
                        not_matched.append(row)
                else:
                    not_matched.append(row)

        db_connection.commit()

for i in not_matched:
    info((i[2], i[1], i[0]))
info("not_matched: {}".format(len(not_matched)))
