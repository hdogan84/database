from os import name
from typing import NamedTuple, List
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from urllib.request import urlopen
from tools.logging import debug, info, error
import csv
import argparse
from math import ceil
from pathlib import Path
from tools.configuration import parse_config
from tools.file_handling.audio import read_parameters_from_audio_file
from datetime import date, datetime
from tools.db import sanitize_name, sanitize_altitude
from tools.db.table_types import (
    XenoCantoRow,
)
from tools.file_handling.csv import write_to_csv
from tools.file_handling.collect import (
    rename_and_copy_to,
)

from tools.db import (
    connectToDB,
    get_entry_id_or_create_it,
    get_id_of_entry_in_table,
    get_synonyms_dict,
)

CONFIG_FILE_PATH = Path("./config_training.cfg")
CSV_FILEPATH = Path("birdsounds.csv")
FILES_DIRECTORY_PATH = Path("/mnt/z/AG/TSA/Mario/_Backups/XenoCantoDisk/sounds/")


def import_xeno_canto(
    files=FILES_DIRECTORY_PATH, config_path=CONFIG_FILE_PATH, csv_path=CSV_FILEPATH
):
    config = parse_config(config_path)
    species_set = set()
   
    record_id_map = {}
    file_map = []
    try:
        with open("map_xeno_db_id.csv", newline="") as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=";", quotechar='"')
            next(csv_reader)
            file_map = [row for row in csv_reader]
            for row in file_map:
                record_id_map[row[0]] = row
    except:
        pass

    with open(csv_path, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        next(csv_reader)
        missed_imports = []

        #print(config.database.host)
        with connectToDB(config.database) as db_connection:
            with db_connection.cursor() as db_cursor:
                db_cursor: MySQLCursor
                counter = 0
                db_cursor.execute("SELECT * FROM species")

                species_table = db_cursor.fetchall()
                species_dict = {}
                for sp in species_table:
                    species_dict[sp[7].lower()] = sp[0]
                    species_dict[sp[8].lower()] = sp[0]
                    species_dict[sp[9].lower()] = sp[0]

                def get_species_id(latin_name: str, english_name: str) -> int:
                    species_id = species_dict.get(latin_name.lower(), None)
                    if species_id is None:
                        species_id = species_dict.get(english_name.lower(), None)
                    #print(species_id)
                    return species_id

                missing_fg = []
                missing_bg = []
                missing_species = {}
                #print(species_dict)
                for row in csv_reader:
                    counter = counter + 1
                    if counter % 10000 == 0:
                        print('commit next {}',counter)
                        # write_to_csv(
                        #     file_map,
                        #     "map_xeno_db_id.csv",
                        #     ["path", "db_id", "duration"],
                        # )
                        # write_to_csv(
                        #     missing_fg, "missing_fg.csv", ["latin_name", "english_name"]
                        # )
                        # write_to_csv(
                        #     missing_bg, "missing_bg.csv", ["latin_name", "english_name"]
                        # )
                        # write_to_csv(missed_imports, "missed_imports.csv", None)

                        db_connection.commit()

                    xeno = XenoCantoRow(*row)
                    xeno: XenoCantoRow
                    species_set.add(
                        ("{} {}".format(xeno.genus, xeno.species), xeno.eng_name)
                    )
                    #synonyms_dict = get_synonyms_dict(db_cursor, "tsa_to_ioc10_1")
                    latin_name = "{} {}".format(xeno.genus, xeno.species)
                    species_id = get_species_id(latin_name, xeno.eng_name)
                    if species_id is None:
                        missed_imports.append(row)
                        if latin_name not in missing_species:
                            missing_species[latin_name]  = True

                        missing_fg.append([latin_name, xeno.eng_name])
                        # error(
                        #     "{} fg {}, {} ".format(counter, latin_name, xeno.eng_name)
                        # )
                        continue
                    # TODO: get File information
                    entry = record_id_map.get(
                        (Path(xeno.dir) / Path(xeno.path)).as_posix(), None
                    )

                    if entry is None:
                        continue
                    record_id = entry[1]
                    duration = entry[2]
                 
                        # file_path = files / Path(xeno.dir) / Path(xeno.path)
                        # if file_path.exists() is False:
                        #     error(
                        #         "File does not exhist {}".format(file_path.as_posix())
                        #     )
                        #     continue
                        # audio_file_parameters = None
                        # try:
                            
                        #     audio_file_parameters = read_parameters_from_audio_file(
                        #         file_path
                        #     )
                        # except:
                        #     error(
                        #         "Could not read audio Parameters from {}".format(
                        #             file_path
                        #         )
                        #     )
                        #     continue

                        # result = get_id_of_entry_in_table(
                        #     db_cursor,
                        #     "record",
                        #     [
                        #         ("md5sum", audio_file_parameters.md5sum),
                        #     ],
                        # )

                        # record_id = result
                        # if record_id is None:
                        #     print("Could not find file for row {}".format(counter))
                        #     continue

                        # file_map.append(
                        #     [
                        #         (Path(xeno.dir) / Path(xeno.path)).as_posix(),
                        #         record_id,
                        #         audio_file_parameters.duration,
                        #     ]
                        # )
                    # create foreground annoation
                    # forground_annoation = [
                    #     ("record_id", record_id),
                    #     ("species_id", species_id),
                    #     ("background", False),
                    #     ("individual_id", None),
                    #     ("group_id", None),
                    #     ("vocalization_type", xeno.songtype),
                    #     ("quality_tag", None),
                    #     ("start_time", 0),
                    #     ("end_time", duration),
                    #     ("start_frequency", None),
                    #     ("end_frequency", None),
                    #     ("channel_ix", None),
                    #     # ("annotator_id", person_id),
                    # ]
                    # print(forground_annoation)
                    # get_entry_id_or_create_it(
                    #     db_cursor,
                    #     "annotation_of_species",
                    #     forground_annoation,
                    #     forground_annoation,
                    # )

                    background_species = xeno.background.split(",")
                    # print(xeno.background)
                    bg_species_ids_map ={}
                    for species in background_species:
                        if not species:
                            continue

                        back_species_id = get_species_id(species, species)
                        if back_species_id is None:
                            missed_imports.append(row)
                            missing_bg.append([latin_name, xeno.eng_name])
                            # error(
                            #     "{} bg {}".format(
                            #         counter, species
                            #     )
                            # )
                            continue
                        bg_species_ids_map[back_species_id] = True
                    # some have english and latin name prevent doubling 
                      
                    for species_bg_id in bg_species_ids_map.keys():
                        background_annoation = [
                            ("record_id", record_id),
                            ("species_id", species_bg_id),
                            ("background", True),
                            ("individual_id", None),
                            ("group_id", None),
                            ("vocalization_type", None),
                            ("quality_tag", None),
                            ("start_time", 0),
                            ("end_time", duration),
                            ("start_frequency", None),
                            ("end_frequency", None),
                            ("channel_ix", None),
                            # ("annotator_id", person_id),
                        ]
                        get_entry_id_or_create_it(
                            db_cursor,
                            "annotation_of_species",
                            background_annoation,
                            background_annoation,
                        )

                # write_to_csv(
                #     file_map, "map_xeno_db_id.csv", ["path", "db_id", "duration"]
                # )
                write_to_csv(
                    missing_fg, "missing_fg.csv", ["latin_name", "english_name"]
                )
                write_to_csv(
                    missing_species.keys(), "missing_species.csv", ["latin_name"]
                )
                write_to_csv(
                    missing_bg, "missing_bg.csv", ["latin_name", "english_name"]
                )
                write_to_csv(missed_imports, "missed_imports.csv", None)
                db_connection.commit()


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--files",
    metavar="path",
    type=Path,
    nargs="?",
    help="target folder",
    default=FILES_DIRECTORY_PATH,
)

parser.add_argument(
    "--csv",
    metavar="path",
    type=Path,
    nargs="?",
    help="csv file with all entries",
    default=CSV_FILEPATH,
)
parser.add_argument(
    "--config",
    metavar="path",
    type=Path,
    nargs="?",
    default=CONFIG_FILE_PATH,
    help="config file with database credentials",
)

args = parser.parse_args()
if __name__ == "__main__":
    import_xeno_canto(files=args.files, config_path=args.config, csv_path=args.csv)
