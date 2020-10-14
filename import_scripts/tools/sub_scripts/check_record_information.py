from mysql.connector import MySQLConnection
from tools.configuration import RecordConfig
from tools.sub_scripts import get_person_id_or_create_it
from tools.sub_scripts import get_equiment_id_or_create_it


def check_record_information(
    db_connection: MySQLConnection, record_information: RecordConfig
) -> bool:

    recordist_id = get_person_id_or_create_it(
        db_connection, record_information.recordist, "Recordist"
    )
    annotator_id = get_person_id_or_create_it(
        db_connection, record_information.annotator, "Annotator"
    )

    equipment_id = get_equiment_id_or_create_it(
        db_connection,
        record_information.equipment,
    )

    print(recordist_id)
    print(annotator_id)
    print(equipment_id)
