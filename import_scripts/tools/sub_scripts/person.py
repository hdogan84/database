import inquirer
from mysql.connector import MySQLConnection
from tools.errors import EntryNotFoundInDbError
from tools.db import get_id_of_entry_in_table, insert_in_table


def get_person_id_or_create_it(
    db_connection: MySQLConnection, person_name: str, person_label: str
) -> int:
    with db_connection.cursor() as db_cursor:
        result = get_id_of_entry_in_table(db_cursor, "person", ("name", person_name))
        if result is None:
            answer = inquirer.confirm(
                "{label} {name} not found do you want to create her/him?".format(
                    label=person_label, name=person_name
                ),
                default=False,
            )
            if answer:
                insert_in_table(
                    db_cursor,
                    "person",
                    [
                        ("name", person_name),
                    ],
                )
                db_connection.commit()
                result = get_id_of_entry_in_table(
                    db_cursor, "person", ("name", person_name)
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
                    raise EntryNotFoundInDbError("person", person_name)
        else:
            return result
