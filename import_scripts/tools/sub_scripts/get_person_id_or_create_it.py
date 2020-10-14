import inquirer
from mysql.connector import MySQLConnection
from tools.errors import EntryNotFoundInDbError
from tools.db import QUERY_FIND_ENTRY_IN_TABLE_BY_NAME, QUERY_INSERT_PERSON


def get_person_id_or_create_it(
    db_connection: MySQLConnection, person_name: str, person_label: str
) -> int:
    with db_connection.cursor() as db_cursor:
        db_cursor.execute(
            QUERY_FIND_ENTRY_IN_TABLE_BY_NAME.format(table="person", name=person_name)
        )
        result = db_cursor.fetchone()
        if result is None:
            answer = inquirer.confirm(
                "{label} {name} not found do you want to create her/him?".format(
                    label=person_label, name=person_name
                ),
                default=False,
            )
            if answer:
                db_cursor.execute(QUERY_INSERT_PERSON.format(name=person_name))
                db_connection.commit()
                db_cursor.execute(
                    QUERY_FIND_ENTRY_IN_TABLE_BY_NAME.format(
                        table="person", name=person_name
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
                    raise EntryNotFoundInDbError("person", person_name)
        else:
            return result[0]
