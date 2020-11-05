from typing import NamedTuple, List
from datetime import date, datetime, time


class BaseEntry:
    id: int
    modified: datetime
    created: datetime
    data: NamedTuple


XenoCantoRow = NamedTuple(
    "XenoCantoRow",
    [
        ("genus", str),
        ("species", str),
        ("ssp", str),
        ("eng_name", str),
        ("family", str),
        ("length_snd", str),
        ("volume_snd", str),
        ("speed_snd", str),
        ("pitch_snd", str),
        ("number_notes_snd", str),
        ("variable_snd", str),
        ("songtype", str),
        ("song_classification", str),
        ("quality", str),
        ("recordist", str),
        ("olddate", str),
        ("date", str),
        ("time", str),
        ("country", str),
        ("location", str),
        ("longitude", str),
        ("latitude", str),
        ("elevation", str),
        ("remarks", str),
        ("background", str),
        ("back_nrs", str),
        ("back_english", str),
        ("back_latin", str),
        ("back_families", str),
        ("back_extra", str),
        ("path", str),
        ("species_nr", str),
        ("order_nr", str),
        ("dir", str),
        ("neotropics", str),
        ("africa", str),
        ("asia", str),
        ("europe", str),
        ("australia", str),
        ("datetime", str),
        ("discussed", str),
        ("license", str),
        ("snd_nr", str),
    ],
)

RecordRowO = NamedTuple(
    "RecordRowI",
    [
        ("date", date),
        ("start", time),
        ("end", time),
        ("duration", float),
        ("sample_rate", int),
        ("bit_depth", int),
        ("channels", int),
        ("mime_type", str),
        ("original_file_name", str),
        ("file_name", str),
        ("md5sum", str),
        ("license", str),
        ("recordist_id", str),
        ("remarks", str),
        ("equipment_id", int),
        ("location_id", int),
        ("collection_id", int),
    ],
)

PersonRowI = NamedTuple(
    "PersonRowI",
    [
        ("name", str),
    ],
)
