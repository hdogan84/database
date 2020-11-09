from _typeshed import NoneType
from os import name
from typing import NamedTuple, List
from mysql.connector.cursor import MySQLCursor
from urllib.request import urlopen
from xmltodict import parse
from tools.logging import debug, info
import csv
from pathlib import Path
from tools.configuration import parse_config
from tools.db.table_types import (
    XenoCantoRow,
    PersonRowI,
    LocationRowI,
    EquipmentRowI,
    CollectionRowI,
    RecordRowI,
    AnnotationI,
)
from tools.db import (
    connectToDB,
    db,
    get_entry_id_or_create_it,
    get_id_of_entry_in_table,
    get_synonyms_dict,
)

"genus", "species", "ssp", "eng_name", "family", "length_snd", "volume_snd", "speed_snd", "pitch_snd", "number_notes_snd", "variable_snd", "songtype", "song_classification", "quality", "recordist", "olddate", "date", "time", "country", "location", "longitude", "latitude", "elevation", "remarks", "background", "back_nrs", "back_english", "back_latin", "back_families", "back_extra", "path", "species_nr", "order_nr", "dir", "neotropics", "africa", "asia", "europe", "australia", "datetime", "discussed", "license", "snd_nr"
CONFIG_FILE_PATH = Path("import_scripts/defaultConfig.cfg")
CSV_FILEPATH = Path("data/birdsounds.csv")
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

            collection_id = get_entry_id_or_create_it(
                db_cursor, "collection", CollectionRowI(name="xeno-canto", remarks=None)
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
                    missed_imports(row)
                    continue
                person_entry = PersonRowI(name=xeno.recordist)

                person_id = get_entry_id_or_create_it(db_cursor, "person", person_entry)

                location_id = get_entry_id_or_create_it(
                    db_cursor,
                    "location",
                    LocationRowI(
                        name=xeno.location,
                        description=None,
                        habitat=None,
                        lat=xeno.latitude,
                        lng=xeno.longitude,
                        altitude=xeno.elevation,
                        remarks=None,
                    ),
                )
                equipment_id = None
                # TODO: get File information
                record_entry = RecordRowI(
                    date=xeno.date,
                    start=xeno.time,
                    end=None,
                    duration=None,
                    sample_rate=None,
                    bit_depth=None,
                    channels=None,
                    mime_type=None,
                    original_file_name=None,
                    file_name=None,
                    md5sum=None,
                    license=xeno.license,
                    recordist_id=person_id,
                    equipment_id=None,
                    location_id=location_id,
                    collection_id=collection_id,
                )

                record_id = get_entry_id_or_create_it(db_cursor, "record", record_entry)
                # create xenocanto link
                get_entry_id_or_create_it(
                    db_cursor,
                    "record_xeno_canto_link",
                    [("record_id", record_id), ("collection_id", xeno.order_nr)],
                )
                # create foreground annoation

                forground_annoation = AnnotationI(
                    record_id=record_id,
                    species_id=species_id,
                    background=False,
                    individual_id=None,
                    group_id=None,
                    vocalization_type=None,
                    quality_tag=None,
                    start_time=0,
                    end_time=None,
                    start_frequency=None,
                    end_frequency=None,
                    channel=None,
                    annotator_id=person_id,
                )