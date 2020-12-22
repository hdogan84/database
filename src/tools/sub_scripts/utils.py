from typing import List, Callable
import inquirer


def ask_for_data(
    values: List[str], validate: List[Callable[[str], bool]] = None
) -> List[str]:
    return list(
        map(
            (
                lambda value_validate_tuple: inquirer.text(
                    "Please enter {label}:".format(label=value_validate_tuple[0]),
                    default="",
                    validate=value_validate_tuple[1],
                )
            ),
            zip(values, validate),
        )
    )


def is_float(_, value: str) -> bool:

    try:
        float(value)
        return True
    except ValueError as _:
        print("\nPlease enter a number")
        return False


def text_max_length(max_length: int) -> Callable[[str], bool]:
    def max_len(_, value: str) -> bool:
        if len(value) <= max_length:
            return True
        else:
            print(
                "\nText is to long it can only be {} characters, but it is {}".format(
                    max_length, len(value)
                )
            )
            return False

    return max_len
