from typing import List
import inquirer
from mysql.connector import MySQLConnection
from tools.errors import EntryNotFoundInDbError
from tools.db import QUERY_INSERT_EQUIPMENT, QUERY_FIND_ENTRY_IN_TABLE_BY_NAME


def inquirer_equipment_data() -> List[str]:

    return list(
        map(
            (
                lambda label: inquirer.text(
                    "Please enter {label}:",
                    default="",
                )
            ),
            ["sound device", "microphone", "remarks"],
        )
    )


def get_equipment_id_or_create_it(
    db_connection: MySQLConnection,
    equipment_name: str,
) -> int:
    with db_connection.cursor() as db_cursor:
        db_cursor.execute(
            QUERY_FIND_ENTRY_IN_TABLE_BY_NAME.format(
                table="equipment", name=equipment_name
            )
        )
        result = db_cursor.fetchone()
        if result is None:
            answer = inquirer.confirm(
                "Equipment {name} not found do you want to create it?",
                default=False,
            )
            if answer:
                data = inquirer_equipment_data()
                db_cursor.execute(
                    QUERY_INSERT_EQUIPMENT.format(
                        name=equipment_name,
                        sound_device=data[0],
                        microphone=data[1],
                        remarks=data[2],
                    )
                )
                db_connection.commit()
                db_cursor.execute(
                    QUERY_FIND_ENTRY_IN_TABLE_BY_NAME.format(
                        table="equipment", name=equipment_name
                    )
                )
                result = db_cursor.fetchone()
                return result[0]
            else:
                answer = inquirer.confirm(
                    "Do you want set null instead?",
                    default=False,
                )
                if answer:
                    return None
                else:
                    raise EntryNotFoundInDbError("equipment", equipment_name)
        else:
            return result[0]
