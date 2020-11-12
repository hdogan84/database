from pathlib import Path
from typing import NamedTuple, List
from pandas import read_csv
from math import isnan

AnnotationRaven = NamedTuple(
    "AnnotationRaven",
    [
        ("channel", int),
        ("start_time", float),
        ("end_time", float),
        ("start_frequency", float),
        ("end_frequency", float),
        ("species_code", str),
        ("individual_id", int),
        ("group_id", int),
        ("vocalization_type", str),
        ("quality_tag", str),
    ],
)

raven_columns = [
    "Channel",
    "Begin Time (s)",
    "End Time (s)",
    "Low Freq (Hz)",
    "High Freq (Hz)",
    "SpeciesCode",
    "Individual_Group",
    "QualityTag",
    "VocalizationTypeCode",
]


def get_group_id(id: str, prefix: str) -> int:

    if isinstance(id, float) and isnan(id):
        return None
    if id.startswith(prefix):
        try:
            return int(id[1:])
        except:
            return None
    return None


def sanitize_quality(quality) -> str:
    if isinstance(quality, str):
        return quality
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
            group_id=get_group_id(row.Individual_Group, "g"),
            vocalization_type=row.vocalization_type,
            quality_tag=None,  # TODO: Ask olaf what format an then fix
        )
        result.append(temp)
    return result
