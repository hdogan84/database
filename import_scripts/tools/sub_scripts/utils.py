from typing import List, Callable
import inquirer


def ask_for_data(
    values: List[str], validate: List[Callable[[str], bool]] = None
) -> List[str]:
    return list(
        map(
            (
                lambda label: inquirer.text(
                    "Please enter {label}:".format(label=label),
                    default="",
                    validate=validate,
                )
            ),
            values,
        )
    )


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError as _:
        return False


def text_max_length(max_length: int) -> Callable[[str], bool]:
    def max_len(value: str) -> bool:
        return len(value) <= max_length

    return max_len
