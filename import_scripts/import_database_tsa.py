from typing import NamedTuple, List
from urllib.request import urlopen
from xmltodict import parse
from typedconfig.source import IniFileConfigSource
from pathlib import Path
from tools.configuration import parse_config
from tools.db import connectToDB, get_entry_id_or_create_it, update_entry
from tools.configuration import DatabaseConfig
import pandas as pd


CONFIG_FILE_PATH = Path("import_scripts/defaultConfig.cfg")

TSA_CONFIG = Path("import_scripts/tsa_connection.cfg")
tsaConfig = DatabaseConfig()
tsaConfig.add_source(IniFileConfigSource(TSA_CONFIG))

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


(
    "AVPDPEAT",
    "AVPIDEMA",
    "AVPDLOCR",
    "AVPDPOPA",
    "AVPDCYCA",
    "AVPDPAMA",
    "AVPCPHSI",
    "AVPCPHTR",
    "AVSYSYAT",
    "AVTGTRTR",
    "AVSISIEU",
    "AVTUTUME",
    "AVTUTUPH",
    "AVTUTUVI",
    "AVMUMUST",
    "AVMUERRU",
    "AVMUFIHY",
    "AVMUPHPH",
    "AVMTANTR",
    "AVFRFRCO",
    "AVFRCOCO",
    "AVFRCHCH",
    "AVFRSPSP",
)
