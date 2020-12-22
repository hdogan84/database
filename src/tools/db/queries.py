from tools.logging import debug
from typing import List, Tuple, Optional, Dict
from mysql.connector import connect, MySQLConnection
from mysql.connector.cursor import MySQLCursor
from pandas.io.formats.format import common_docstring
from tools.configuration import DatabaseConfig
from tools.db.base_queries import (
    insert_in_table,
    get_entries_from_table,
    get_entries_from_table,
)


def get_id_of_entry_in_table(
    db_cursor: MySQLCursor, table: str, field_value_pairs: List[Tuple[str, any]]
) -> Optional[int]:
    debug(
        """get_id_of_entry_in_table: table:{} 
    field_value_pairs: {}""".format(
            table,
            field_value_pairs,
        )
    )
    result = get_entries_from_table(
        db_cursor, table, ["id"], field_value_pairs, only_one=True
    )
    return None if result is None else result[0]


def get_entry_id_or_create_it(
    db_cursor: MySQLCursor,
    table: str,
    query: List[Tuple[str, any]],
    data: List[Tuple[str, any]],
    info: bool = False,
) -> int or Tuple[int, bool]:
    debug(
        """get_entry_id_or_create_it: table:{} 
    query: {}
    data: {}""".format(
            table, query, data
        )
    )
    result = get_id_of_entry_in_table(db_cursor, table, query)
    if result is None:
        insert_in_table(db_cursor, table, data)
        result = get_id_of_entry_in_table(db_cursor, table, query)
        return (result, True) if info else result
    return (result, False) if info else result


def is_annoation_in_database(
    db_cursor: MySQLCursor,
    annotation_table,
    sound_type_field,
    sound_type_field_id=None,
    channel: int = None,
    start_time: float = None,
    end_time: float = None,
    start_frequency: float = None,
    end_frequency: float = None,
) -> bool:
    parts = [
        (sound_type_field, sound_type_field_id),
        ("channel", channel),
        ("start_time", start_time),
        ("end_time", end_time),
        ("start_frequency", start_frequency),
        ("end_frequency", end_frequency),
    ]
    result = get_entries_from_table(
        db_cursor, annotation_table, ["id"], parts, only_one=True
    )
    return False if result is None else True


def get_synonyms_dict(db_cursor: MySQLCursor, synonym_field: str) -> Dict[str, str]:
    debug("get_synonyms db:cursor_type".format(type(db_cursor)))
    query = """
    SELECT `{field}`,species_id FROM species_synonyms WHERE `{field}` IS NOT NULL
    """.format(
        field=synonym_field
    )
    db_cursor.execute(query)
    result = db_cursor.fetchall()
    return dict(result)
