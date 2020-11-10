from os import name
from typing import NamedTuple, List
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from urllib.request import urlopen
from xmltodict import parse
from tools.logging import debug, info, error
import csv
from math import ceil
from pathlib import Path
from tools.configuration import parse_config
from tools.file_handling.audio import read_parameters_from_audio_file
from datetime import date, datetime
from tools.db.table_types import (
    XenoCantoRow,
)

from tools.db import (
    connectToDB,
    get_entry_id_or_create_it,
    get_id_of_entry_in_table,
    get_synonyms_dict,
)

CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")
CSV_FILEPATH = Path("database/data/birdsounds.csv")
FILES_DIRECTORY_PATH = Path(
    "/home/bewr/external-volumes/stana/mnt/z/AG/TSA/Mario/_Backups/XenoCantoDisk/sounds/"
)
config = parse_config(CONFIG_FILE_PATH)
species_set = set()


def get_species_id(latin_name: str, english_name: str) -> int:
    species_id = get_id_of_entry_in_table(
        db_cursor, "species", [("latin_name", latin_name)]
    )
    if species_id is None:
        species_id = get_id_of_entry_in_table(
            db_cursor, "species", [("english_name", english_name)]
        )
    return species_id


with open(CSV_FILEPATH, newline="") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
    next(csv_reader)
    missed_imports = []
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor

            collection_entry = [("name", "xeno-canto"), ("remarks", None)]
            collection_id = get_entry_id_or_create_it(
                db_cursor, "collection", collection_entry, collection_entry
            )
            counter = 0
            for row in csv_reader:
                try:
                    counter = counter + 1
                    if counter > 3:
                        break
                    xeno = XenoCantoRow(*row)
                    xeno: XenoCantoRow
                    species_set.add(
                        ("{} {}".format(xeno.genus, xeno.species), xeno.eng_name)
                    )
                    synonyms_dict = get_synonyms_dict(db_cursor, "tsa_to_ioc10.1")
                    latin_name = "{} {}".format(xeno.genus, xeno.species)
                    species_id = get_species_id(latin_name, xeno.eng_name)
                    if species_id is None:
                        missed_imports.append(row)
                        error(
                            "Could not identify species{}, {} ".format(
                                latin_name, xeno.eng_name
                            )
                        )
                        continue
                    # TODO: get File information
                    file_path = FILES_DIRECTORY_PATH / Path(xeno.dir) / Path(xeno.path)
                    if file_path.exists() is False:
                        error("File does not exhist {}".format(file_path.as_posix()))
                        continue

                    audio_file_parameters = read_parameters_from_audio_file(file_path)
                    person_entry = [("name", xeno.recordist)]
                    person_id = get_entry_id_or_create_it(
                        db_cursor, "person", person_entry, person_entry
                    )

                    location_entry = [
                        ("name", xeno.location),
                        ("description", None),
                        ("habitat", None),
                        ("lat", xeno.latitude),
                        ("lng", xeno.longitude),
                        ("altitude", xeno.elevation),
                        ("remarks", None),
                    ]
                    location_id = get_entry_id_or_create_it(
                        db_cursor, "location", location_entry, location_entry
                    )
                    db_connection.commit()
                    equipment_id = None
                    record_start = datetime.strptime(xeno.time, "%H:%M")
                    record_entry = [
                        ("date", xeno.date),
                        ("start", record_start.time()),
                        (
                            "end",
                            (
                                record_start
                                + timedelta(
                                    seconds=ceil(audio_file_parameters.duration)
                                )
                            ).time(),
                        ),
                        ("duration", audio_file_parameters.duration),
                        ("sample_rate", audio_file_parameters.sample_rate),
                        ("bit_depth", audio_file_parameters.bit_depth),
                        ("bit_rate", audio_file_parameters.bit_rate),
                        ("channels", audio_file_parameters.channels),
                        ("mime_type", audio_file_parameters.mime_type),
                        (
                            "original_file_name",
                            audio_file_parameters.original_file_name,
                        ),
                        ("file_name", audio_file_parameters.file_name),
                        ("md5sum", audio_file_parameters.md5sum),
                        ("license", xeno.license),
                        ("recordist_id", person_id),
                        ("equipment_id", None),
                        ("location_id", location_id),
                        ("collection_id", collection_id),
                    ]

                    record_id = get_entry_id_or_create_it(
                        db_cursor,
                        "record",
                        [
                            ("md5sum", audio_file_parameters.md5sum),
                        ],
                        record_entry,
                    )
                    # create xenocanto link
                    xeno_canto_link_data = [
                        ("record_id", record_id),
                        ("collection_id", xeno.order_nr),
                    ]
                    get_entry_id_or_create_it(
                        db_cursor,
                        "record_xeno_canto_link",
                        xeno_canto_link_data,
                        xeno_canto_link_data,
                    )
                    # create foreground annoation

                    forground_annoation = [
                        ("record_id", record_id),
                        ("species_id", species_id),
                        ("background", False),
                        ("individual_id", None),
                        ("group_id", None),
                        ("vocalization_type", None),
                        ("quality_tag", None),
                        ("start_time", 0),
                        ("end_time", None),
                        ("start_frequency", None),
                        ("end_frequency", None),
                        ("channel", None),
                        ("annotator_id", person_id),
                    ]
                except:
                    break
