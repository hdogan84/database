from pathlib import Path
from typing import Collection, Dict, List
from math import ceil, modf
from mysql.connector import MySQLConnection
from datetime import date, timedelta
from mysql.connector.cursor import MySQLCursor
from tools.logging import debug, info, error
from tools.db.queries import get_id_of_entry_in_table
from tools.file_handling.collect import (
    rename_and_copy_to,
)
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


CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")

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

DATA_PATH = Path(
    "/home/bewr/external-volumes/stana/mnt/z/AG/TSA/Mario/_Backups/TsaOrgTrainAudioData/"
)

COLLECTIONS = [
    ("CD014", "VogelCDs", True),
    ("CD043", "VogelCDs", True),
    ("CD041", "VogelCDs", True),
    ("CD058", "VogelCDs", True),
    ("CD124", "VogelCDs", True),
    ("CD126", "VogelCDs", True),
    ("CD127", "VogelCDs", True),
    ("CD901", "VogelCDs", True),
    ("CD097", "VogelCDs", True),
    ("CD123", "VogelCDs", True),
    ("CD001", "VogelCDs", True),
    ("CD002", "VogelCDs", True),
    ("CD003", "VogelCDs", True),
    ("CD004", "VogelCDs", True),
    ("Nachtigall01", "Nachtigall01", True),
    ("TsaJorn", "TsaJorn", True),
    ("RefSys", "RefSys", False),
    ("TsaShorts", "Shorts", False),
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
):
    db_cursor_tsa.execute(
        """SELECT 
        Date, /* 0 */
        Time, /* 1 */ 
        Duration, /* 2 */ 
        SrcFileName, /* 3 */ 
        Recordist, /* 4 */ 
        Country, /* 5 */ 
        Locality, /* 6 */ 
        Latitude, /* 7 */ 
        Longitude, /* 8 */ 
        Elevation, /* 9 */
        Quality, /* 10 */
        FileName, /* 11 */
        ClassName, /* 12 */
        SoundType /* 13 */
        FROM train_europe_v02 
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
        audio_filepath = DATA_PATH.joinpath(collection_path).joinpath(row[11] + ".wav")
        if audio_filepath.exists() is False:
            error("File does not exhist {}".format(audio_filepath.as_posix()))
            return
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
            ("start", time),
            (
                "end",
                end,
            ),
            (
                "duration",
                row[2],
            ),
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
        # db_connection_la.commit()
        # if created:
        #     targetDirectory = orginal_path.joinpath(target_record_file_path)
        #     targetDirectory.mkdir(parents=True, exist_ok=True)
        #     rename_and_copy_to(
        #         audio_filepath,
        #         targetDirectory,
        #         audio_file_parameters.filename,
        #     )

        #     # remove all old annotations
        #     delete_from_table(
        #         db_cursor_la, "annotation_of_species", [("record_id", record_id)]
        #     )
        #     db_connection_la.commit()

        species_id = get_id_of_entry_in_table(
            db_cursor_la, "species", [("latin_name", row[12])]
        )
        if species_id is None:
            failed_annotations.append(
                (row[12], audio_file_parameters.original_filename)
            )
            info("Missing species {}", row[12])
            continue

        annoation_data = [
            ("record_id", record_id),
            ("species_id", species_id),
            ("individual_id", None),
            ("group_id", None),
            ("vocalization_type", row[13]),
            ("quality_tag", row[10]),
            ("id_level", 1),
            ("channel", audio_file_parameters.channels),
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
        # db_connection_la.commit()

    # # to distinct species values

    for fa in failed_annotations:
        if fa[0] not in failed_species_labels:
            failed_species_labels.update({fa[0]: "\t" + fa[1]})
        else:
            failed_species_labels.update({fa[0]: labels.get(fa[0]) + "\n \t" + fa[1]})

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
