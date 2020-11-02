from typing import NamedTuple, List
from urllib.request import urlopen
from xmltodict import parse
from typedconfig.source import IniStringConfigSource
from pathlib import Path
from tools.configuration import parse_config
from tools.db import connectToDB, get_entry_id_or_create_it, update_entry
from tools.configuration import DatabaseConfig
import pandas as pd


CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

TSA_CONFIG = """
[database]
user = root
host = localhost
port = 3307
password = pass2root
name = tsa_data
file_storage_path = /tmp/
"""
tsaConfig = DatabaseConfig()
tsaConfig.add_source(IniStringConfigSource(TSA_CONFIG))

config = parse_config(CONFIG_FILE_PATH)


# get species list with codes from majo from train_europe table
SELECT_DISTINCT_SPECIES = """
SELECT DISTINCT ClassName, ClassId FROM train_europe_v02 
ORDER BY ClassName ASC;
"""

species_train_collection = []
with connectToDB(tsaConfig) as db_tsa_connection:
    with db_tsa_connection.cursor() as db_tsa_cursor:
        db_tsa_cursor.execute(SELECT_DISTINCT_SPECIES)
        species_train_collection = db_tsa_cursor.fetchall()

not_matched = []
with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        for row in species_train_collection:
            result = update_entry(
                db_cursor,
                "species",
                [("mario_id", row[1])],
                [("latin_name", row[0])],
            )
            if db_cursor.rowcount is 0:
                not_matched.append(row)
        db_connection.commit()

for i in not_matched:
    print(i[0])
print("not_matched: {}".format(len(not_matched)))
