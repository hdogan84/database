from typing import NamedTuple, List
from urllib.request import urlopen
from xmltodict import parse

from pathlib import Path
from tools.configuration import parse_config
from tools.db import connectToDB, get_entry_id_or_create_it


SpeciesRow = NamedTuple(
    "SpeciesRow",
    [
        ("order_latin", str),
        ("family_latin", str),
        ("genus_latin", str),
        ("species_latin", str),
        ("english_name", str),
    ],
)

CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")
XML_URI = "http://www.worldbirdnames.org/master_ioc-names_xml.xml"

config = parse_config(CONFIG_FILE_PATH)

print("Download xml from {}".format(XML_URI))
var_url = urlopen(XML_URI)
print("Start parsing XML")
xmldoc = parse(var_url)
species_rows: List[SpeciesRow] = []
print("Start parsing XML")
for order in xmldoc["ioclist"]["list"]["order"]:
    order_name = order["latin_name"]
    families = (
        order["family"] if isinstance(order["family"], list) else [order["family"]]
    )
    for family in families:
        family_name = family["latin_name"]
        genus_list = (
            family["genus"] if isinstance(family["genus"], list) else [family["genus"]]
        )
        for genus in genus_list:
            genus_name = genus["latin_name"]
            species_list = (
                genus["species"]
                if isinstance(genus["species"], list)
                else [genus["species"]]
            )
            for species in species_list:
                species_name = species["latin_name"]
                english_name = species["english_name"]
                speciesInfos = SpeciesRow(
                    order_latin=order_name,
                    family_latin=family_name,
                    genus_latin=genus_name,
                    species_latin=species_name,
                    english_name=english_name,
                )
                species_rows.append(speciesInfos)
sorted_species: List[SpeciesRow] = sorted(
    species_rows,
    key=lambda row: "{}{}{}{}".format(
        row.order_latin, row.family_latin, row.genus_latin, row.species_latin
    ),
)
print(len(sorted_species))


with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        for row_data in sorted_species:

            data = [
                ("order", row_data.order_latin),
                ("family", row_data.family_latin),
                ("genus", row_data.genus_latin),
                ("species", row_data.species_latin),
                (
                    "latin_name",
                    "{} {}".format(row_data.genus_latin, row_data.species_latin),
                ),
                ("english_name", row_data.english_name),
            ]

            record_id = get_entry_id_or_create_it(
                db_cursor,
                "species",
                [
                    (
                        "latin_name",
                        "{} {}".format(row_data.genus_latin, row_data.species_latin),
                    )
                ],
                data=data,
            )
    db_connection.commit()
