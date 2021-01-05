import csv
from typing import List


def write_to_csv(data: list, filename: str, header: List[str]) -> None:
    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(
            csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(header)
        csv_writer.writerows(data)
