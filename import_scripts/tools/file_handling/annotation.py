from pathlib import Path
from typing import NamedTuple, List
from pandas import read_csv


AnnotationRaven = NamedTuple(
    "AnnotationRaven",
    [
        ("index", int),
        ("channel", int),
        ("start_time", float),
        ("end_time", float),
        ("start_frequency", float),
        ("end_frequency", float),
        ("species_code", str),
    ],
)

raven_columns = [
    "Channel",
    "Begin Time (s)",
    "End Time (s)",
    "Low Freq (Hz)",
    "High Freq (Hz)",
    "SpeciesCode",
]


def read_raven_file(file: Path) -> List[AnnotationRaven]:
    print(file)
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
        }
    )
    result: List[AnnotationRaven] = []
    for row in annotations.itertuples():
        result.append(AnnotationRaven(*row))
    return result
