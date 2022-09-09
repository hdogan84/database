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

RecordRowI = NamedTuple(
    "RecordRowI",
    [
        ("date", date),
        ("time", time),
        #("end", time),
        ("duration", float),
        ("sample_rate", int),
        ("bit_depth", int),
        ("channels", int),
        ("mime_type", str),
        ("original_filename", str),
        ("filename", str),
        ("md5sum", str),
        ("license", str),
        ("recordist_id", str),
        ("remarks", str),
        ("equipment_id", int),
        ("location_id", int),
        ("collection_id", int),
    ],
)

LocationRowI = NamedTuple(
    "LocationRowI",
    [
        ("name", str),
        ("description", str),
        ("habitat", str),
        ("lat", float),
        ("lng", float),
        ("altitude", float),
        ("remarks", str),
    ],
)

CollectionRowI = NamedTuple(
    "CollectionRowI",
    [("name", str), ("remarks", str)],
)


EquipmentRowI = NamedTuple(
    "EquipmentRowI",
    [("name", str), ("sound_device", str), ("mirophone", str), ("remarks", str)],
)

AnnotationI = NamedTuple(
    "AnnotationI",
    [
        ("record_id", int),
        ("species_id", int),
        ("background", bool),
        ("individual_id", int),
        ("group_id", int),
        ("vocalization_type", str),
        ("quality_tag", int),
        ("start_time", float),
        ("end_time", float),
        ("start_frequency", int),
        ("end_frequency", int),
        ("channel_ix", int),
        ("annotator_id", int),
    ],
)