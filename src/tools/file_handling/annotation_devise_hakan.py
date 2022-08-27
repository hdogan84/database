from pathlib import Path
from typing import NamedTuple, List
from pandas import read_csv
from math import isnan
from functools import cmp_to_key

from enum import Enum
from math import isnan

annotation_interval = "annotation_interval"
BACKGROUND = "BG"


from decimal import Decimal, ROUND_HALF_EVEN

# AnnotationRaven = NamedTuple(
#     "AnnotationRaven",
#     [
#         ("channel: int),
#         ("start_time", float),
#         ("end_time", float),
#         ("start_frequency", float),
#         ("end_frequency", float),
#         ("species_code", str),
#         ("individual_id", int),
#         ("group_id", int),
#         ("vocalization_type", str),
#         ("quality_tag", str),
#     ],
# )


class AnnotationDeviseExcel:
    filename: str
    species_code: str
    collection_id: str
    channel: int
    start_time: float
    end_time: float
    sub_dir: str

    def __init__(
        self, filename, species_code, channel, start_time, end_time, sub_dir,
    ):
        self.channel = channel
        self.start_time = start_time
        self.end_time = end_time
        self.species_code = species_code
        # self.individual_id = individual_id
        # self.group_id = group_id
        # self.vocalization_type = vocalization_type
        # self.quality_tag = quality_tag
        # self.best_channel = best_channel


def speciesCodeToInt(code: str) -> int:
    if code == annotation_interval:
        return 0
    if code == BACKGROUND:
        return 1
    else:
        return 2


def channel_code_to_int(code: str) -> int:
    if code == "ch1":
        return 0
    if code == "ch2":
        return 1
    if code == "ch3":
        return 2
    if code == "ch4":
        return 3
    return None


def compareRows(x: AnnotationDeviseExcel, y: AnnotationDeviseExcel) -> int:
    x_start_time = Decimal(x.start_time).quantize(
        Decimal(".000001"), rounding=ROUND_HALF_EVEN
    )
    y_start_time = Decimal(y.start_time).quantize(
        Decimal(".000001"), rounding=ROUND_HALF_EVEN
    )
    x_end_time = Decimal(x.end_time).quantize(
        Decimal(".000001"), rounding=ROUND_HALF_EVEN
    )
    y_end_time = Decimal(y.end_time).quantize(
        Decimal(".000001"), rounding=ROUND_HALF_EVEN
    )
    if x_start_time < y_start_time:
        return -1
    if x_start_time > y_start_time:
        return 1
    else:
        if x_end_time < y_end_time:
            return 1
        if x_end_time > y_end_time:
            return -1
        else:
            if x.species_code == "TD_Start_End":
                return -1
            if y.species_code == "TD_Start_End":
                return 1
            xc = speciesCodeToInt(x.species_code)
            yc = speciesCodeToInt(y.species_code)
            if xc < yc:
                return -1
            if xc > yc:
                return 1
            else:
                return 0


excel_columns = [
    "filename",
    "class",
    "collection_id",
    "channel_ix",
    "start_time",
    "end_time",
    "sub_dir",
]


def read_raven_file(file: Path) -> List[AnnotationDeviseExcel]:
    annotations = read_csv(
        open(file, "rb"),
        delimiter="\t",
        encoding="unicode_escape",
        usecols=excel_columns,
    )

    annotations = annotations.rename(
        columns={
            "filename": "filename",
            "class": "species_code",
            "collection_id": "collection_id",
            "channel_ix": "channel",
            "start_time": "start_time",
            "end_time": "end_time",
            "sub_dir": "sub_dir",
        }
    )

    result: List[AnnotationDeviseExcel] = []
    for row in annotations.itertuples():
        temp = AnnotationDeviseExcel(
            channel=row.channel - 1,
            start_time=row.start_time,
            end_time=row.end_time,
            species_code=row.species_code,
        )
        result.append(temp)
    sortedRows = sorted(result, key=cmp_to_key(compareRows))
    quality = None
    for row in sortedRows:  # add quality code
        if row.species_code == annotation_interval:
            quality = None
        else:
            if row.species_code == BACKGROUND:
                quality = row.quality_tag
            else:
                row.quality_tag = quality

    return list(filter(lambda x: x.species_code != BACKGROUND, sortedRows,))

