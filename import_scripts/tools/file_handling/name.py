from typing import NamedTuple
from datetime import date, time, datetime

FileNameInformations = NamedTuple(
    "FileNameInformations_name_date_time",
    [
        ("location_name", str),
        ("record_date", date),
        ("record_time", time),
    ],
)


def parse_file_name_for_location_date_time(file_name: str) -> FileNameInformations:
    parts = file_name.split(sep="_", maxsplit=1)
    location_name = parts[0]
    record_datetime = datetime.strptime(parts[1], "%Y%m%d_%H%M%S")
    return FileNameInformations(
        location_name=location_name,
        record_date=record_datetime.date(),
        record_time=record_datetime.time(),
    )
