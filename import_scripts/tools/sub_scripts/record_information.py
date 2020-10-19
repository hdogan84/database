from mysql.connector import MySQLConnection
from tools.configuration import RecordConfig
from tools.sub_scripts.equipment import get_equipment_id_or_create_it
from tools.sub_scripts.location import get_location_id_or_create_it
from tools.sub_scripts.person import get_person_id_or_create_it


def check_record_information(
    db_connection: MySQLConnection, record_information: RecordConfig
) -> bool:

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

    print(recordist_id)
    print(annotator_id)
    print(equipment_id)
    print(location_id)
