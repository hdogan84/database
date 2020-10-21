from pathlib import Path
from math import ceil
from datetime import timedelta
from mysql.connector import connect
from tools.file_handling.collect import get_record_annoation_tupels_from_directory
from tools.file_handling.name import parse_file_name_for_location_date_time
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config
from tools.sub_scripts.record_information import check_get_ids_from_record_informations
from tools.file_handling.annotation import read_raven_file
from tools.db import get_entry_id_or_create_it, insert_in_table

DATA_PATH = Path("database/data/BD_Background")
CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

RECORD_MERGE_STRATEGY = "merge"
ANOTATION_STRATEGY = "merge"
ANNOTATION_TABLE = "species"
LICENSE = None

if CONFIG_FILE_PATH.exists() is False:
    raise FileNotFoundError(CONFIG_FILE_PATH)
if DATA_PATH.is_dir() is False:
    raise FileNotFoundError(DATA_PATH)

config = parse_config(CONFIG_FILE_PATH)
list_of_files = get_record_annoation_tupels_from_directory(
    DATA_PATH,
    record_file_ending=config.files.record_file_ending,
    annoation_file_ending=config.files.annoation_file_ending,
)

# check if all filenames are valid
for corresponding_files in list_of_files:
    _ = parse_file_name_for_location_date_time(corresponding_files.audio_file.stem)
    read_parameters_from_audio_file(corresponding_files.audio_file)
    read_raven_file(corresponding_files.annoation_file)


with connect(
    host=config.database.host,
    port=config.database.port,
    user=config.database.user,
    passwd=config.database.password,
    database=config.database.name,
    auth_plugin="mysql_native_password",
) as db_connection:
    import_meta_ids = check_get_ids_from_record_informations(
        db_connection, config.record_information
    )
    # start import files
    with db_connection.cursor() as db_cursor:
        for corresponding_files in list_of_files:
            file_name_infos = parse_file_name_for_location_date_time(
                corresponding_files.audio_file.stem
            )
            file_parameters = read_parameters_from_audio_file(
                corresponding_files.audio_file
            )

            record_data = [
                ("date", file_name_infos.record_datetime.strftime("%Y-%m-%d")),
                ("start", file_name_infos.record_datetime.time()),
                (
                    "end",
                    (
                        file_name_infos.record_datetime
                        + timedelta(seconds=ceil(file_parameters.duration))
                    ).time(),
                ),
                (
                    "duration",
                    file_parameters.duration,
                ),
                ("sample_rate", file_parameters.sample_rate),
                ("bit_depth", file_parameters.bit_depth),
                ("channels", file_parameters.channels),
                ("mime_type", file_parameters.mime_type),
                ("original_file_name", file_parameters.original_file_name),
                ("file_name", file_parameters.file_name),
                ("md5sum", file_parameters.md5sum),
                ("quality", None),
                ("location_id", import_meta_ids.location_id),
                ("recordist_id", import_meta_ids.recordist_id),
                ("equipment_id", import_meta_ids.equipment_id),
                ("license", LICENSE),
            ]
            record_id = get_entry_id_or_create_it(
                db_cursor,
                "record",
                [("md5sum", file_parameters.md5sum)],
                data=record_data,
            )

            annotations = read_raven_file(corresponding_files.annoation_file)
            for a in annotations:
                # TODO: get id of species
                annoation_data = [
                    ("record_id", record_id),
                    ("channel", a.channel),
                    ("start_time", a.start_time),
                    ("end_time", a.end_time),
                    ("start_frequency", a.start_frequency),
                    ("end_frequency", a.end_frequency),
                    ("annotator_id", import_meta_ids.annotator_id),
                ]

                get_entry_id_or_create_it(
                    db_cursor,
                    "annotation_of_species",
                    query=annoation_data,
                    data=annoation_data,
                )
            db_connection.commit()
        # read_raven_file(corresponding_files.annoation_file)
