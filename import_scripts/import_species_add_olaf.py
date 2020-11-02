from typing import NamedTuple, List
from urllib.request import urlopen
from xmltodict import parse

from pathlib import Path
from tools.configuration import parse_config
from tools.db import connectToDB, get_entry_id_or_create_it, update_entry
import pandas as pd

XLSX_FILE_PATH = "database/AMMOD_AV_20201023_CNN_Training_v4.xlsx"
CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

config = parse_config(CONFIG_FILE_PATH)
DF = pd.read_excel(XLSX_FILE_PATH)
selection = DF[
    ["6LetterCode_IOC10.1_New", "GermanName_DOG2019", "ScientificName_DOG2019"]
]
not_matched = []
with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        for index, row in selection.iterrows():
            result = update_entry(
                db_cursor,
                "species",
                [("german_name", row[1]), ("olaf_id", row[0])],
                [("latin_name", row[2])],
            )
            if db_cursor.rowcount is 0:
                not_matched.append(row)
        db_connection.commit()

for i in not_matched:
    print(i[2])
print("not_matched: {}".format(len(not_matched)))
