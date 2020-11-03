import inquirer
from mysql.connector import MySQLConnection
from tools.errors import EntryNotFoundInDbError
from tools.db import get_id_of_entry_in_table, insert_in_table


def get_collection_id_or_create_it(
    db_connection: MySQLConnection, collection_name: str, label: str
) -> int:
    with db_connection.cursor() as db_cursor:
        result = get_id_of_entry_in_table(
            db_cursor, "collection", [("name", collection_name)]
        )
        if result is None:
            answer = inquirer.confirm(
                "{label} {name} not found do you want to create it?".format(
                    label=label, name=collection_name
                ),
            )
            if answer:
                insert_in_table(
                    db_cursor,
                    "collection",
                    [
                        ("name", collection_name),
                    ],
                )
                db_connection.commit()
                result = get_id_of_entry_in_table(
                    db_cursor, "collection", [("name", collection_name)]
                )
                return result
            else:
                answer = inquirer.confirm(
                    "Do you want set null instead?",
                )
                if answer:
                    return None
                else:
                    raise EntryNotFoundInDbError("collection", collection_name)
        else:
            return result
