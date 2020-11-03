from typing import List, Tuple, Optional
from mysql.connector import connect, MySQLConnection
from pandas.io.formats.format import common_docstring
from tools.configuration import DatabaseConfig

QUERY_FIND_IN_TABLE_BY_VALUES = """
SELECT id FROM {table} WHERE {condition};
"""

QUERY_INSERT_IN_TABLE = """
INSERT INTO {table} ({keys}) VALUES ({values})
"""

QUERY_UPDATE_IN_TABLE = """
UPDATE {table} SET {values} WHERE {condition}; 
"""


def __to_sql(value):
    if value is None:
        return "null"
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return str(round(value, 6))
    if isinstance(value, str):
        return value
    return "{}".format(value)


def __to_Condition(field_value_pairs: List[Tuple[str, any]]) -> str:
    condition = " and ".join(
        list(map(lambda x: "`{}`={}".format(x[0], "%s"), field_value_pairs))
    )
    return condition


def __to_key_equals_values(field_value_pairs: List[Tuple[str, any]]) -> str:
    condition = " , ".join(
        list(map(lambda x: "`{}`={}".format(x[0], "%s"), field_value_pairs))
    )
    return condition


def get_id_of_entry_in_table(
    db_cursor: any, table: str, field_value_pairs: List[Tuple[str, any]]
) -> Optional[int]:

    query = QUERY_FIND_IN_TABLE_BY_VALUES.format(
        table=table, condition=__to_Condition(field_value_pairs)
    )
    db_cursor.execute(query, tuple(__to_sql(i[1]) for i in field_value_pairs))
    result = db_cursor.fetchone()
    return None if result is None else result[0]


def insert_in_table(
    db_cursor: any, table: str, field_value_pairs: List[Tuple[str, any]]
) -> None:
    """
    Query will not be commited, You have to commit the query by yourself
    """
    keys = ", ".join(["`{}`".format(x[0]) for x in field_value_pairs])
    values = ", ".join(list(map(lambda x: "%s", field_value_pairs)))
    query = QUERY_INSERT_IN_TABLE.format(table=table, keys=keys, values=values)
    db_cursor.execute(query, tuple(__to_sql(i[1]) for i in field_value_pairs))


def update_entry(
    db_cursor: any,
    table: str,
    values: List[Tuple[str, any]],
    condition: List[Tuple[str, any]],
) -> None:
    query = QUERY_UPDATE_IN_TABLE.format(
        table=table,
        condition=__to_Condition(condition),
        values=__to_key_equals_values(values),
    )

    db_cursor.execute(query, tuple(__to_sql(i[1]) for i in (values + condition)))


def get_entry_id_or_create_it(
    db_cursor: any,
    table: str,
    query: List[Tuple[str, any]],
    data: List[Tuple[str, any]],
) -> int:
    result = get_id_of_entry_in_table(db_cursor, table, query)
    if result is None:
        insert_in_table(db_cursor, table, data)
        result = get_id_of_entry_in_table(db_cursor, table, query)
    return result


def is_annoation_in_database(
    db_cursor: any,
    annotation_table,
    sound_type_field,
    sound_type_field_id=None,
    channel: int = None,
    start_time: float = None,
    end_time: float = None,
    start_frequency: float = None,
    end_frequency: float = None,
) -> bool:
    query = """
SELECT id FROM {table} WHERE {field} = '{field_id}' {querypart}
"""
    parts = [
        (sound_type_field, sound_type_field_id),
        ("channel", channel),
        ("start_time", start_time),
        ("end_time", end_time),
        ("start_frequency", start_frequency),
        ("end_frequency", end_frequency),
    ]
    querypart = ", ".join(
        list(map(lambda x: " and {}='{}'".format(x[0], __to_sql(x[1])), parts))
    )
    db_cursor.execute(
        query.format(
            table=annotation_table,
            field=sound_type_field,
            field_id=sound_type_field_id,
            querypart=querypart,
        )
    )
    result = db_cursor.fetchone()
    return False if result is None else True


def connectToDB(config: DatabaseConfig) -> MySQLConnection:
    return connect(
        host=config.host,
        port=config.port,
        user=config.user,
        passwd=config.password,
        database=config.name,
        auth_plugin="mysql_native_password",
    )
