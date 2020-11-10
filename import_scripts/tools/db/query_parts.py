from typing import List, Tuple
from tools.db.helpers import to_sql_save_value
from tools.logging import debug


def to_and_condition(field_value_pairs: List[Tuple[str, any]]) -> str:
    part = " and ".join(
        list(
            map(
                lambda x: "`{}` {} {}".format(
                    x[0], "is" if x[1] is None else "=", "%s"
                ),
                field_value_pairs,
            )
        )
    )
    return part


def to_key_value_list(field_value_pairs: List[Tuple[str, any]]) -> str:
    part = " , ".join(
        list(
            map(
                lambda x: "`{}` {} {}".format(
                    x[0], "is" if x[1] is None else "=", "%s"
                ),
                field_value_pairs,
            )
        )
    )
    return part


def to_key_list(field_value_pairs: List[Tuple[str, any]]) -> str:
    part = " , ".join(list(map(lambda x: "`{}`".format(x[0]), field_value_pairs)))
    return part


def to_placeholder_list(field_value_pairs: List[Tuple[str, any]]) -> str:
    part = " , ".join(list(map(lambda x: "%s", field_value_pairs)))
    return part


def to_sql_save_value_list(field_value_pairs: List[Tuple[str, any]]) -> str:
    result = tuple(to_sql_save_value(i[1]) for i in field_value_pairs)

    return result
