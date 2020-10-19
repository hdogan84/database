from typing import List, Tuple, Optional

QUERY_FIND_IN_TABLE_BY_VALUE = """
SELECT id FROM {table} WHERE {key} = '{value}';
"""

QUERY_INSERT_IN_TABLE = """
INSERT INTO {table} ({keys}) VALUES ({values})
"""


def get_id_of_entry_in_table(
    db_cursor: any, table: str, field_value_pair: Tuple[str, any]
) -> Optional[int]:

    db_cursor.execute(
        QUERY_FIND_IN_TABLE_BY_VALUE.format(
            table=table, key=field_value_pair[0], value=field_value_pair[1]
        )
    )
    result = db_cursor.fetchone()
    return None if result is None else result[0]


def insert_in_table(
    db_cursor: any, table: str, field_value_pairs: List[Tuple[str, any]]
) -> None:
    """
    Query will not be commited, You have to commit the query by yourself
    """
    keys = ", ".join([x[0] for x in field_value_pairs])
    values = ", ".join(list(map(lambda x: "'{}'".format(x[1]), field_value_pairs)))
    print(QUERY_INSERT_IN_TABLE.format(table=table, keys=keys, values=values))
    db_cursor.execute(
        QUERY_INSERT_IN_TABLE.format(table=table, keys=keys, values=values)
    )
