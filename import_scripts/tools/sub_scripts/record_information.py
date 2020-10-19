import typing
from mysql.connector import MySQLConnection
from tools.configuration import RecordConfig
from tools.sub_scripts.equipment import get_equipment_id_or_create_it
from tools.sub_scripts.location import get_location_id_or_create_it
from tools.sub_scripts.person import get_person_id_or_create_it


RecordInformaionIds = typing.NamedTuple(
    "RecordInformaionIds",
    [
        ("annotator_id", int),
        ("recordist_id", int),
        ("equipment_id", int),
        ("location_id", int),
    ],
)


def check_get_ids_from_record_informations(
    db_connection: MySQLConnection, record_information: RecordConfig
) -> RecordInformaionIds:

    annotator_id = get_person_id_or_create_it(
        db_connection, record_information.annotator, "Annotator"
    )
    recordist_id = get_person_id_or_create_it(
        db_connection, record_information.recordist, "Recordist"
    )

    equipment_id = get_equipment_id_or_create_it(
        db_connection,
        record_information.equipment,
    )

    location_id = get_location_id_or_create_it(
        db_connection,
        record_information.location,
    )

    return RecordInformaionIds(
        recordist_id=recordist_id,
        annotator_id=annotator_id,
        equipment_id=equipment_id,
        location_id=location_id,
    )
