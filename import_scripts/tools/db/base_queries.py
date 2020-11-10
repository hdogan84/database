from os import WUNTRACED
from tools.errors import MoreThanOneEntryInDbError
from typing import List, Tuple
from mysql.connector.cursor import MySQLCursor
from tools.db.query_parts import (
    to_and_condition,
    to_key_list,
    to_key_value_list,
    to_placeholder_list,
    to_sql_save_value_list,
)
from tools.logging import debug

QUERY_FIND_IN_TABLE_BY_VALUES = """
SELECT id FROM {table} WHERE {condition};
"""

QUERY_INSERT_IN_TABLE = """
INSERT INTO {table} ({fields}) VALUES ({values})
"""

QUERY_UPDATE_IN_TABLE = """
UPDATE {table} SET {values} WHERE {condition}; 
"""
QUERY_SELECT_ENTRY_FROM_TABLE_BY_VALUES = """
SELECT {fields} FROM {table} WHERE {condition};
"""


def get_entries_from_table(
    db_cursor: MySQLCursor,
    table: str,
    fields: List[str],
    field_value_pairs: List[Tuple[str, any]],
    only_one=False,
) -> Tuple:

    condition = to_and_condition(field_value_pairs)
    query = QUERY_SELECT_ENTRY_FROM_TABLE_BY_VALUES.format(
        table=table, fields=",".join(fields), condition=condition
    )
    debug("get_entries_from_table query: {}".format(query))
    debug(
        "get_entries_from_table query parameters:",
    )

    db_cursor.execute(query, to_sql_save_value_list(field_value_pairs))
    results = db_cursor.fetchmany(size=2)
    debug("get_entries_from_table result: {}".format(results))
    if only_one:
        if len(results) == 0:
            return None
        if len(results) > 1:
            raise MoreThanOneEntryInDbError(table, field_value_pairs)
        return results[0]
    return results


def insert_in_table(
    db_cursor: MySQLCursor, table: str, field_value_pairs: List[Tuple[str, any]]
) -> None:
    """
    Query will not be commited, You have to commit the query by yourself
    """
    fields = to_key_list(field_value_pairs)
    values = to_placeholder_list(field_value_pairs)
    query = QUERY_INSERT_IN_TABLE.format(table=table, fields=fields, values=values)
    db_cursor.execute(query, to_sql_save_value_list(field_value_pairs))


def update_entry(
    db_cursor: MySQLCursor,
    table: str,
    values: List[Tuple[str, any]],
    condition: List[Tuple[str, any]],
) -> None:
    query = QUERY_UPDATE_IN_TABLE.format(
        table=table,
        condition=to_and_condition(condition),
        values=to_key_value_list(values),
    )
    db_cursor.execute(query, to_sql_save_value_list(values + condition))
