from pathlib import Path
from typing import Collection, Dict, List
from math import ceil, modf
from mysql.connector import MySQLConnection
from datetime import date, timedelta
from mysql.connector.cursor import MySQLCursor
from tools.logging import debug, info, error
from tools.db.queries import get_id_of_entry_in_table
from tools.file_handling.collect import rename_and_copy_to
from datetime import datetime
from tools.file_handling.name import parse_filename_for_location_date_time
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config, DatabaseConfig
from typedconfig.source import IniStringConfigSource
from tools.sub_scripts.record_information import check_get_ids_from_record_informations
from tools.file_handling.annotation import read_raven_file
from tools.db import (
    get_entry_id_or_create_it,
    connectToDB,
    delete_from_table,
    sanitize_name,
    sanitize_altitude,
)
from tools.TSA_Species_Translator import TSA_Species_Translator

from tools.logging import info
import argparse


class TSADB:
    classId = 0
    className = 1
    fileName = 2
    collection = 3
    soundType = 4
    duration = 5
    recordist = 6
    country = 7
    locality = 8
    elevation = 9
    date = 10
    time = 11
    quality = 12
    backgroundSpecies = 13
    srcFileName = 14
    remarks = 15
    created = 16
    modified = 17
    dbId = 17


db = TSADB()


CONFIG_FILE_PATH = Path("config.cfg")

TSA_CONFIG = """
[database]
user = root
host = localhost
port = 3306
password = pass2root
name = tsa_data
file_storage_path = /tmp/
"""
tsaConfig = DatabaseConfig()
tsaConfig.add_source(IniStringConfigSource(TSA_CONFIG))

DATA_PATH = Path("/mnt/z/AG/TSA/Mario/_Backups/TsaOrgTrainAudioData/")
TEST_RUN = True
# CollectionName, SubFolders,
COLLECTIONS = [
    ("TsaShorts", "ShortsAll", False),
    # ("CD014", "VogelCDs", False),
    # ("CD043", "VogelCDs", False),
    # ("CD041", "VogelCDs", False),
    # ("CD058", "VogelCDs", False),
    # ("CD124", "VogelCDs", False),
    # ("CD126", "VogelCDs", False),
    # ("CD127", "VogelCDs", False),
    # ("CD901", "VogelCDs", False),
    # ("CD097", "VogelCDs", False),
    # ("CD123", "VogelCDs", False),
    # ("CD001", "VogelCDs", False),
    # ("CD002", "VogelCDs", False),
    # ("CD003", "VogelCDs", False),
    # ("CD004", "VogelCDs", False),
    # ("Nachtigall01", "Nachtigall01", False),
    # ("TsaJorn", "TsaJorn", False),
    # ("RefSys", "RefSys", False),
]


def import_data(data_path=DATA_PATH, config_file_path=CONFIG_FILE_PATH) -> List[str]:
    config = parse_config(config_file_path)

    info("Load Data from database")
    failed_species_labels = {}
    with connectToDB(tsaConfig) as db_connection_tsa, connectToDB(
        config.database
    ) as db_connection_la:
        with db_connection_tsa.cursor(buffered=True) as db_cursor_tsa:
            with db_connection_la.cursor(buffered=True) as db_cursor_la:
                species_translator = TSA_Species_Translator(db_cursor_la)
                for collection in COLLECTIONS:
                    info("Import collection {}".format(collection))
                    collection_entry = [
                        ("name", collection[0]),
                        ("remarks", None),
                    ]
                    collection_id = get_entry_id_or_create_it(
                        db_cursor_la, "collection", collection_entry, collection_entry
                    )

                    labels = do_collection_data_import(
                        db_connection_la,
                        db_cursor_tsa,
                        db_cursor_la,
                        collection[0],
                        collection_id,
                        collection[1],
                        collection[2],
                        config.database.get_originals_files_path(),
                        failed_species_labels,
                        species_translator,
                        data_path,
                    )
    info(failed_species_labels)


def do_collection_data_import(
    db_connection_la: MySQLConnection,
    db_cursor_tsa: MySQLCursor,
    db_cursor_la: MySQLCursor,
    collection: str,
    collection_id: int,
    collection_path: str,
    use_src_filename: bool,
    orginal_path: Path,
    failed_species_labels,
    species_translator: TSA_Species_Translator,
    data_path: Path,
):
    db_cursor_tsa.execute(
        """SELECT 
        t1.Date, /* 0 */
        t1.Time, /* 1 */ 
        t1.Duration, /* 2 */ 
        t1.SrcFileName, /* 3 */ 
        t1.Recordist, /* 4 */ 
        t1.Country, /* 5 */ 
        t1.Locality, /* 6 */ 
        t1.Latitude, /* 7 */ 
        t1.Longitude, /* 8 */ 
        t1.Elevation, /* 9 */
        t1.Quality, /* 10 */
        t1.FileName, /* 11 */
        t1.ClassName, /* 12 */
        t1.SoundType, /* 13 */
        t2.English_Name /*14*/
        FROM train_europe_v02 as t1
        LEFT JOIN system as t2 on t1.ClassName = t2.Artname
        WHERE Collection = %s""",
        (collection,),
    )
    failed_annotations = []
    count = db_cursor_tsa.rowcount
    data = db_cursor_tsa.fetchall()
    i = 0
    for row in data:
        if i % 100 == 0:
            info("imported {}/{}".format(i, count))
        i = i + 1

        if use_src_filename:
            audio_filepath = data_path.joinpath(collection_path).joinpath(row[3])
        else:
            audio_filepath = data_path.joinpath(collection_path).joinpath(
                row[11] + ".wav"
            )

        if audio_filepath.exists() is False:
            error("File does not exhist {}".format(audio_filepath.as_posix()))
            continue

        audio_file_parameters = None
        try:
            audio_file_parameters = read_parameters_from_audio_file(audio_filepath)
        except:
            error("Could not read audio Parameters from {}".format(audio_filepath))
            continue
        target_record_file_path = "{}/{}/{}".format(
            audio_file_parameters.md5sum[0],
            audio_file_parameters.md5sum[1],
            audio_file_parameters.md5sum[2],
        )
        person_entry = [("name", sanitize_name(row[4], 128))]
        person_id = get_entry_id_or_create_it(
            db_cursor_la, "person", person_entry, person_entry
        )
        location_entry = [
            ("name", sanitize_name("{} {}".format(row[5], row[6]), 256)),
            ("description", None),
            ("habitat", None),
            ("lat", row[7]),
            ("lng", row[8]),
            ("altitude", row[9]),
            ("remarks", None),
        ]
        # print(location_entry)
        location_id = get_entry_id_or_create_it(
            db_cursor_la,
            "location",
            [
                ("name", location_entry[0][1]),
                ("description", None),
                ("habitat", None),
                ("remarks", None),
            ],
            location_entry,
        )

        time = None
        end = None

        if row[1] is not None and row[0] is not None:
            timestamp = datetime.combine(row[0], datetime.min.time()) + row[1]
            time = timestamp.time()
            end = timestamp + timedelta(seconds=ceil(row[2]))

        record_data = [
            ("date", row[0]),
            ("time", time),
            #("end", end,),
            ("duration", row[2],),
            ("sample_rate", audio_file_parameters.sample_rate),
            ("bit_depth", audio_file_parameters.bit_depth),
            ("bit_rate", audio_file_parameters.bit_rate),
            ("channels", audio_file_parameters.channels),
            ("mime_type", audio_file_parameters.mime_type),
            ("original_filename", audio_file_parameters.original_filename),
            ("filename", audio_file_parameters.filename),
            ("file_path", target_record_file_path),
            ("md5sum", audio_file_parameters.md5sum),
            ("location_id", location_id),
            ("recordist_id", person_id),
            ("equipment_id", None),
            ("collection_id", collection_id),
            ("license", None),
        ]
        (record_id, created) = get_entry_id_or_create_it(
            db_cursor_la,
            "record",
            [("md5sum", audio_file_parameters.md5sum)],
            data=record_data,
            info=True,
        )
        if TEST_RUN is False:
            db_connection_la.commit()
            if created:
                targetDirectory = orginal_path.joinpath(target_record_file_path)
                targetDirectory.mkdir(parents=True, exist_ok=True)
                rename_and_copy_to(
                    audio_filepath, targetDirectory, audio_file_parameters.filename,
                )

                # remove all old annotations
                delete_from_table(
                    db_cursor_la, "annotation_of_species", [("record_id", record_id)]
                )
                print("File Copyied {}".format(audio_file_parameters.filename))
                db_connection_la.commit()

        species_id = species_translator.get_species_id(db_cursor_la, row[12], row[14])
        if species_id is None:
            failed_annotations.append(row[12])
            info("Missing species {}", (row[12]))
            continue

        annoation_data = [
            ("record_id", record_id),
            ("species_id", species_id),
            ("individual_id", None),
            ("group_id", None),
            ("vocalization_type", None),
            ("quality_tag", row[10]),
            ("id_level", 1),
            ("channel_ix", audio_file_parameters.channels),
            ("start_time", 0),
            ("end_time", row[2]),
            ("start_frequency", None),
            ("end_frequency", None),
            ("annotator_id", person_id),
        ]

        get_entry_id_or_create_it(
            db_cursor_la,
            "annotation_of_species",
            query=annoation_data,
            data=annoation_data,
        )
        if TEST_RUN is False:
            db_connection_la.commit()

    # # to distinct species values
    failed_species_labels.update(set(failed_annotations))

    info("Failed annotations not matched species {}".format(len(failed_annotations)))
    # # read_raven_file(corresponding_files.annoation_file)

    return failed_species_labels


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--data",
    metavar="path",
    type=Path,
    nargs="?",
    help="target folder",
    default=DATA_PATH,
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
    import_data(args.data, args.config)
