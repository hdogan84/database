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


def santize_altitude(value: str):
    result = value.strip()
    if result.startswith("<"):
        result = result.split("<")[1]
    tmp = result.split("-")
    if len(tmp) > 1:
        result = int(tmp[0])
    if result == "?" or result == "NULL":
        return None
    try:
        return int(result)
    except:
        return None


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

            for row in csv_reader:
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
                    (
                        "lat",
                        None
                        if xeno.latitude == "?" or xeno.latitude == "NULL"
                        else xeno.latitude,
                    ),
                    (
                        "lng",
                        None
                        if xeno.longitude == "?" or xeno.longitude == "NULL"
                        else xeno.longitude,
                    ),
                    (
                        "altitude",
                        santize_altitude(xeno.elevation),
                    ),
                    ("remarks", None),
                ]
                print(location_entry)
                location_id = get_entry_id_or_create_it(
                    db_cursor,
                    "location",
                    [
                        ("name", xeno.location),
                        ("description", None),
                        ("habitat", None),
                        ("remarks", None),
                    ],
                    location_entry,
                )
                db_connection.commit()
                equipment_id = None
                print(xeno.time)
                record_start = (
                    None
                    if xeno.time == "?" or "?:?"
                    else datetime.strptime(xeno.time, "%H:%M")
                )
                print(xeno.date)
                dateParts = xeno.date.split("-")
                dateParts[1] = "01" if dateParts[1] == "00" else dateParts[1]
                dateParts[2] = "01" if dateParts[2] == "00" else dateParts[2]

                record_entry = [
                    ("date", "-".join(dateParts)),
                    (
                        "start",
                        record_start if record_start is None else record_start.time(),
                    ),
                    (
                        "end",
                        record_start
                        if record_start is None
                        else (
                            record_start
                            + timedelta(seconds=ceil(audio_file_parameters.duration))
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
                    ("collection_id", xeno.snd_nr),
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
                    ("vocalization_type", xeno.songtype),
                    ("quality_tag", None),
                    ("start_time", 0),
                    ("end_time", audio_file_parameters.duration),
                    ("start_frequency", None),
                    ("end_frequency", None),
                    ("channel", None),
                    ("annotator_id", person_id),
                ]
                print(forground_annoation)
                get_entry_id_or_create_it(
                    db_cursor,
                    "annotation_of_species",
                    forground_annoation,
                    forground_annoation,
                )

                background_species = xeno.background.split(",")
                for species in background_species:
                    back_species_id = get_species_id(latin_name, xeno.eng_name)
                    if back_species_id is None:
                        missed_imports.append(row)
                        error(
                            "Could not identify species{}, {} ".format(
                                latin_name, xeno.eng_name
                            )
                        )
                        continue
                    background_annoation = [
                        ("record_id", record_id),
                        ("species_id", species_id),
                        ("background", True),
                        ("individual_id", None),
                        ("group_id", None),
                        ("vocalization_type", None),
                        ("quality_tag", None),
                        ("start_time", 0),
                        ("end_time", audio_file_parameters.duration),
                        ("start_frequency", None),
                        ("end_frequency", None),
                        ("channel", None),
                        ("annotator_id", person_id),
                    ]
                    get_entry_id_or_create_it(
                        db_cursor,
                        "annotation_of_species",
                        background_annoation,
                        background_annoation,
                    )
                # db_connection.commit()
