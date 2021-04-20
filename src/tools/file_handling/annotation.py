from pathlib import Path
from typing import NamedTuple, List
from pandas import read_csv
from math import isnan
from functools import cmp_to_key

from enum import Enum
from math import isnan

TD_START_END = "TD_Start_End"
BACKGROUND = "BACKGROUND"


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


class AnnotationRaven:
    channel: int
    start_time: float
    end_time: float
    start_frequency: float
    end_frequency: float
    species_code: str
    individual_id: int
    group_id: int
    vocalization_type: str
    quality_tag: str
    id_level: int

    def __init__(
        self,
        channel,
        start_time,
        end_time,
        start_frequency,
        end_frequency,
        species_code,
        individual_id,
        group_id,
        vocalization_type,
        quality_tag,
        id_level,
    ):
        self.channel = channel
        self.start_time = start_time
        self.end_time = end_time
        self.start_frequency = start_frequency
        self.end_frequency = end_frequency
        self.species_code = species_code
        self.individual_id = individual_id
        self.group_id = group_id
        self.vocalization_type = vocalization_type
        self.quality_tag = quality_tag
        self.id_level = id_level


def speciesCodeToInt(code: str) -> int:
    if code == TD_START_END:
        return 0
    if code == BACKGROUND:
        return 1
    else:
        return 2


def compareRows(x: AnnotationRaven, y: AnnotationRaven) -> int:
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
            return -1
        if x_end_time > y_end_time:
            return 1
        else:
            xc = speciesCodeToInt(x.species_code)
            yc = speciesCodeToInt(y.species_code)
            if xc < yc:
                return -1
            if xc > yc:
                return 1
            else:
                return 0


raven_columns = [
    "Channel",
    "Begin Time (s)",
    "End Time (s)",
    "Low Freq (Hz)",
    "High Freq (Hz)",
    "SpeciesCode",
    "Individual_Group",
    "ID_level",
    "QualityTag",
    "VocalizationTypeCode",
]


def get_group_id(id: str, prefixes: str) -> int:

    if isinstance(id, float) and isnan(id):
        return None
    for prefix in prefixes if isinstance(prefixes, List) else [prefixes]:
        if id.startswith(prefix):
            try:
                return int(id[1:])
            except:
                return None
    return None


def sanitize_quality(quality) -> str:
    if isinstance(quality, str) and quality != "NULL":
        return quality
    else:
        return None


def sanitize_id_level(id_level) -> int:
    if isinstance(id_level, str) and id_level != "NULL":
        return int(id_level[-1])
    else:
        return None


def read_raven_file(file: Path) -> List[AnnotationRaven]:
    annotations = read_csv(
        open(file, "rb"),
        delimiter="\t",
        encoding="unicode_escape",
        usecols=raven_columns,
    )

    annotations = annotations.rename(
        columns={
            "Index": "index",
            "Channel": "channel",
            "Begin Time (s)": "start_time",
            "End Time (s)": "end_time",
            "Low Freq (Hz)": "start_frequency",
            "High Freq (Hz)": "end_frequency",
            "SpeciesCode": "species_code",
            "ID_level": "id_level",
            "QualityTag": "quality_tag",
            "VocalizationTypeCode": "vocalization_type",
        }
    )

    result: List[AnnotationRaven] = []
    for row in annotations.itertuples():
        temp = AnnotationRaven(
            channel=row.channel,
            start_time=row.start_time,
            end_time=row.end_time,
            start_frequency=row.start_frequency,
            end_frequency=row.end_frequency,
            species_code=row.species_code,
            individual_id=get_group_id(row.Individual_Group, "i"),
            group_id=get_group_id(row.Individual_Group, ["g", "f", "m"]),
            id_level=sanitize_id_level(row.id_level),
            vocalization_type=row.vocalization_type,
            quality_tag=sanitize_quality(
                row.quality_tag
            ),  # TODO: Ask olaf what format an then fix
        )
        result.append(temp)
    sortedRows = sorted(result, key=cmp_to_key(compareRows))
    quality = None
    for row in sortedRows:  # add quality code
        if row.species_code == TD_START_END:
            quality = None
        else:
            if row.species_code == BACKGROUND:
                quality = row.quality_tag
            else:
                row.quality_tag = quality

    return list(filter(lambda x: x.species_code != BACKGROUND, sortedRows,))

