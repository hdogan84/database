from typing import NamedTuple, List
from mysql.connector.cursor import MySQLCursor
from urllib.request import urlopen
from xmltodict import parse
from tools.logging import debug, info
import csv
from pathlib import Path
from tools.configuration import parse_config
from tools.db.table_types import XenoCantoRow, PersonRowO
from tools.db import (
    connectToDB,
    get_entry_id_or_create_it,
    get_id_of_entry_in_table,
    get_synonyms_dict,
)


CONFIG_FILE_PATH = Path("import_scripts/defaultConfig.cfg")
CSV_FILEPATH = Path("data/birdsounds.csv")
config = parse_config(CONFIG_FILE_PATH)
species_set = set()

with open(CSV_FILEPATH, newline="") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
    next(csv_reader)
    missed_imports = []
    with connectToDB(config.database) as db_concd.nection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor
            for row in csv_reader:
                xeno = XenoCantoRow(*row)
                xeno: XenoCantoRow
                species_set.add(
                    ("{} {}".format(xeno.genus, xeno.species), xeno.eng_name)
                )
                synonyms_dict = get_synonyms_dict(db_cursor, "tsa_to_ioc10.1")
                latin_name = "{} {}".format(xeno.genus, xeno.species)
                species_id = get_id_of_entry_in_table(
                    db_cursor, "species", [("latin_name", latin_name)]
                )
                if species_id is None:
                    species_id = get_id_of_entry_in_table(
                        db_cursor, "species", [("english_name", xeno.eng_name)]
                    )
                    if species_id is None:
                        missed_imports(row)
                        continue
                person_entry = PersonRowO(name=xeno.recordist)

                person_id = get_entry_id_or_create_it(db_cursor, "person", person_entry)


info(len(missed_imports))