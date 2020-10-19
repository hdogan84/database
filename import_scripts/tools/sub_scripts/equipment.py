import inquirer
from mysql.connector import MySQLConnection
from tools.errors import EntryNotFoundInDbError
from tools.db import get_id_of_entry_in_table, insert_in_table
from tools.sub_scripts.utils import ask_for_data, text_max_length


def get_equipment_id_or_create_it(
    db_connection: MySQLConnection,
    equipment_name: str,
) -> int:
    with db_connection.cursor() as db_cursor:
        result = get_id_of_entry_in_table(
            db_cursor, "equipment", ("name", equipment_name)
        )

        if result is None:
            answer = inquirer.confirm(
                "Equipment {name} not found do you want to create it?".format(
                    name=equipment_name
                ),
                default=False,
            )
            if answer:
                data = ask_for_data(
                    ["sound device", "microphone", "remarks"],
                    validate=[
                        text_max_length(64),
                        text_max_length(64),
                        text_max_length(65535),
                    ],
                )
                insert_in_table(
                    db_cursor,
                    "equipment",
                    [
                        ("name", equipment_name),
                        ("sound_device", data[0]),
                        ("microphone", data[1]),
                        ("remarks", data[2]),
                    ],
                )
                db_connection.commit()
                result = get_id_of_entry_in_table(
                    db_cursor, "equipment", ("name", equipment_name)
                )
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
            return result
