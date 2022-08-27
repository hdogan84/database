import logging
import sys
from logging import *

basicConfig(level=logging.INFO)


def progbar(curr, total, full_progbar, end=""):
    frac = curr / total
    filled_progbar = round(frac * full_progbar)
    print(
        "\r",
        "#" * filled_progbar + "-" * (full_progbar - filled_progbar),
        "[{:>7.2%}]".format(frac),
        end=end,
    )
    if curr == total:
        print("\n")
    sys.stdout.flush()
