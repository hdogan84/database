from pathlib import Path
from typing import Dict, List
from math import ceil
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from tools.db.queries import get_id_of_entry_in_table
from tools.file_handling.collect import (
    get_record_annoation_tupels_from_directory,
    rename_and_copy_to,
)
from tools.file_handling.name import parse_filename_for_location_date_time
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config
from tools.sub_scripts.record_information import check_get_ids_from_record_informations
from tools.file_handling.annotation import read_raven_file
from tools.db import (
    get_entry_id_or_create_it,
    connectToDB,
    delete_from_table,
)
from tools.logging import info

DATA_PATH = Path("libro_animalis/data/TD_Training")
CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")


RECORD_MERGE_STRATEGY = "merge"
ANOTATION_STRATEGY = "merge"
ANNOTATION_TABLE = "species"
LICENSE = None


def import_data(data_path=DATA_PATH, config_file_path=CONFIG_FILE_PATH) -> List[str]:
    config = parse_config(config_file_path)
    list_of_files = get_record_annoation_tupels_from_directory(
        data_path,
        record_file_ending=config.files.record_file_ending,
        annoation_file_ending=config.files.annoation_file_ending,
    )

    # check if all filenames are valid
    info("Start checking files")
    for corresponding_files in list_of_files:

        _ = parse_filename_for_location_date_time(corresponding_files.audio_file.stem)
        read_parameters_from_audio_file(corresponding_files.audio_file)
        read_raven_file(corresponding_files.annoation_file)

    info("Start importing files")
    with connectToDB(config.database) as db_connection:
        import_meta_ids = check_get_ids_from_record_informations(
            db_connection, config.record_information
        )
        # start import files
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor
            failed_annotations = []
            collection_entry = [
                ("name", import_meta_ids.collection_id),
                ("remarks", None),
            ]
            collection_id = get_entry_id_or_create_it(
                db_cursor, "collection", collection_entry, collection_entry
            )
            for corresponding_files in list_of_files:
                filename_infos = parse_filename_for_location_date_time(
                    corresponding_files.audio_file.stem
                )
                file_parameters = read_parameters_from_audio_file(
                    corresponding_files.audio_file
                )

                record_data = [
                    ("date", filename_infos.record_datetime.strftime("%Y-%m-%d")),
                    ("start", filename_infos.record_datetime.time()),
                    (
                        "end",
                        (
                            filename_infos.record_datetime
                            + timedelta(seconds=ceil(file_parameters.duration))
                        ).time(),
                    ),
                    (
                        "duration",
                        file_parameters.duration,
                    ),
                    ("sample_rate", file_parameters.sample_rate),
                    ("bit_depth", file_parameters.bit_depth),
                    ("bit_rate", file_parameters.bit_rate),
                    ("channels", file_parameters.channels),
                    ("mime_type", file_parameters.mime_type),
                    ("original_filename", file_parameters.original_filename),
                    ("filename", file_parameters.filename),
                    ("md5sum", file_parameters.md5sum),
                    ("location_id", import_meta_ids.location_id),
                    ("recordist_id", import_meta_ids.recordist_id),
                    ("equipment_id", import_meta_ids.equipment_id),
                    ("collection_id", collection_id),
                    ("license", LICENSE),
                ]
                (record_id, created) = get_entry_id_or_create_it(
                    db_cursor,
                    "record",
                    [("md5sum", file_parameters.md5sum)],
                    data=record_data,
                    info=True,
                )

                db_connection.commit()
                if created:
                    rename_and_copy_to(
                        corresponding_files.audio_file,
                        config.database.get_originals_files_path(),
                        file_parameters.filename,
                    )

                # remove all old annotations
                delete_from_table(
                    db_cursor, "annotation_of_species", [("record_id", record_id)]
                )
                db_connection.commit()

                annotations = read_raven_file(corresponding_files.annoation_file)

                for a in annotations:
                    # TODO: get id of species
                    species_id = get_id_of_entry_in_table(
                        db_cursor, "species", [("olaf8_id", a.species_code)]
                    )
                    if species_id is None:
                        failed_annotations.append(
                            (a.species_code, file_parameters.original_filename)
                        )
                        continue

                    annoation_data = [
                        ("record_id", record_id),
                        ("species_id", species_id),
                        ("individual_id", a.individual_id),
                        ("group_id", a.group_id),
                        ("vocalization_type", a.vocalization_type),
                        ("quality_tag", a.quality_tag),
                        ("id_level", a.id_level),
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

            # to distinct species values
            labels = {}
            for fa in failed_annotations:
                if fa[0] not in labels:
                    labels.update({fa[0]: "\t" + fa[1]})
                else:
                    labels.update({fa[0]: labels.get(fa[0]) + "\n \t" + fa[1]})

            # for x in labels:
            #     print(x)
            # print(labels[x])

            info(
                "Failed annotations not matched species {}".format(
                    len(failed_annotations)
                )
            )
            # read_raven_file(corresponding_files.annoation_file)
            return labels


if __name__ == "__main__":
    import_data()