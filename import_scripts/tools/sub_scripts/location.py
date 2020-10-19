import inquirer
from mysql.connector import MySQLConnection
from tools.errors import EntryNotFoundInDbError
from tools.db import (
    get_id_of_entry_in_table,
    insert_in_table,
)
from tools.sub_scripts.utils import ask_for_data, is_float, text_max_length


def get_location_id_or_create_it(
    db_connection: MySQLConnection,
    location_name: str,
) -> int:
    with db_connection.cursor() as db_cursor:

        result = get_id_of_entry_in_table(
            db_cursor, "location", ("name", location_name)
        )

        if result is None:
            answer = inquirer.confirm(
                "Location {name} not found do you want to create it?".format(
                    name=location_name
                ),
                default=False,
            )
            if answer:
                data = ask_for_data(
                    ["description", "habitat", "lat", "lng", "remarks"],
                    validate=[
                        text_max_length(65535),
                        text_max_length(64),
                        is_float,
                        is_float,
                        text_max_length(65535),
                    ],
                )
                insert_in_table(
                    db_cursor,
                    "location",
                    [
                        ("name", location_name),
                        ("description", data[0]),
                        ("habitat", data[1]),
                        ("lat", data[2]),
                        ("lng", data[3]),
                        ("remarks", data[4]),
                    ],
                )
                db_connection.commit()
                result = get_id_of_entry_in_table(
                    db_cursor, "location", ("name", location_name)
                )
                return result
            else:
                answer = inquirer.confirm(
                    "Do you want set null instead?",
                    default=False,
                )
                if answer:
                    return None
                else:
                    raise EntryNotFoundInDbError("location", location_name)
        else:
            return result
