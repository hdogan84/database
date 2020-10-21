from typing import List, Tuple, Optional

QUERY_FIND_IN_TABLE_BY_VALUES = """
SELECT id FROM {table} WHERE {condition};
"""

QUERY_INSERT_IN_TABLE = """
INSERT INTO {table} ({keys}) VALUES ({values})
"""


def to_sql(value):
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(round(value, 6))
    return "'{}'".format(value)


def get_id_of_entry_in_table(
    db_cursor: any, table: str, field_value_pairs: List[Tuple[str, any]]
) -> Optional[int]:
    condition = " and ".join(
        list(map(lambda x: "{}={}".format(x[0], to_sql(x[1])), field_value_pairs))
    )
    query = QUERY_FIND_IN_TABLE_BY_VALUES.format(table=table, condition=condition)
    print(query)
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return None if result is None else result[0]


def insert_in_table(
    db_cursor: any, table: str, field_value_pairs: List[Tuple[str, any]]
) -> None:
    """
    Query will not be commited, You have to commit the query by yourself
    """
    keys = ", ".join([x[0] for x in field_value_pairs])
    values = ", ".join(list(map(lambda x: to_sql(x[1]), field_value_pairs)))

    query = QUERY_INSERT_IN_TABLE.format(table=table, keys=keys, values=values)

    print("insert in {}".format(table))
    db_cursor.execute(query)


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
        list(map(lambda x: " and {}='{}'".format(x[0], to_sql(x[1])), parts))
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
