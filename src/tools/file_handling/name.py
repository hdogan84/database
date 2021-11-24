from typing import NamedTuple
from datetime import date, datetime

FileNameInformations = NamedTuple(
    "FileNameInformations_name_date_time",
    [("location_name", str), ("record_datetime", date),],
)


def parse_datetime(date_string):
    try:
        return datetime.strptime(date_string, "%Y%m%d_%H%M%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(date_string, "%y%m%d_%H%M%S")
    except ValueError:
        pass
    return datetime.strptime(date_string, "Y%m%d_%H%M%S00")


def parse_filename_for_location_date_time(filename: str) -> FileNameInformations:
    parts = filename.replace("-", "_").split(sep="_", maxsplit=1)

    location_name = parts[0]
    record_datetime = ""

    if len(parts[1].split(sep="_")) > 2:
        subparts = parts[1].split(sep="_")
        record_datetime = parse_datetime("{}_{}".format(subparts[0], subparts[1]))

    else:
        record_datetime = parse_datetime(parts[1])

    return FileNameInformations(
        location_name=location_name, record_datetime=record_datetime,
    )
