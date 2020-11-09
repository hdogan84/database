from typing import NamedTuple, List
from urllib.request import urlopen
from xmltodict import parse

from pathlib import Path
from tools.configuration import parse_config
from tools.db import connectToDB, get_entry_id_or_create_it
import pandas as pd


SpeciesRow = NamedTuple(
    "SpeciesRow",
    [
        ("order_latin", str),
        ("family_latin", str),
        ("genus_latin", str),
        ("species_latin", str),
        ("english_name", str),
        ("german_name", str),
    ],
)


def import_from_Xml(fileURL: str) -> List[SpeciesRow]:
    print("Download xml from {}".format(fileURL))
    var_url = urlopen(fileURL)
    print("Start parsing XML")
    xmldoc = parse(var_url, process_namespaces=True)
    species_rows: List[SpeciesRow] = []
    print("Start generating rows")
    orders = xmldoc["ioclist"]["list"]["order"]

    for order in orders:
        order_name = order["latin_name"]
        families = (
            order["family"] if isinstance(order["family"], list) else [order["family"]]
        )

        for family in families:
            family_name = family["latin_name"]
            genus_list = (
                family["genus"]
                if isinstance(family["genus"], list)
                else [family["genus"]]
            )

            # print(len(genus_list))
            for genus in genus_list:
                genus_name = genus["latin_name"]
                species_list = (
                    genus["species"]
                    if isinstance(genus["species"], list)
                    else [genus["species"]]
                )
                # print(len(species_list))
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
        return sorted_species


def import_from_multilanguage_excel(filePath: Path):
    df = pd.read_excel(filePath)
    df = df.rename(
        columns={
            "Unnamed: 4": "english_name",
            "Scientific Name": "latin_name",
            "German": "german_name",
            "Order": "order",
            "Family": "family",
        },
    )
    df["english_name"] = df["english_name"].shift(-1)
    selection = df[["order", "family", "latin_name", "german_name", "english_name"]]
    selection["order"] = selection["order"].ffill(axis=0)
    selection["family"] = selection["family"].ffill(axis=0)
    selection = selection.dropna()
    selection[["genus", "species"]] = selection["latin_name"].str.split(
        " ", expand=True
    )

    return selection.sort_values(by=["order", "family", "genus", "species"])


CONFIG_FILE_PATH = Path("import_scripts/defaultConfig.cfg")
# XML_URI = "http://www.worldbirdnames.org/master_ioc-names_xml.xml"
EXCEL_FILEPATH = Path("data/Multiling IOC 10.1.xlsx")

config = parse_config(CONFIG_FILE_PATH)
sorted_species = import_from_multilanguage_excel(EXCEL_FILEPATH)

with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        for _, row_data in sorted_species.iterrows():

            data = [
                ("order", "Aves"),
                ("order", row_data["order"]),
                ("family", row_data["family"]),
                ("genus", row_data["genus"]),
                ("species", row_data["species"]),
                ("sub_species", None),
                ("latin_name", row_data["latin_name"]),
                ("english_name", row_data["english_name"]),
                ("german_name", row_data["german_name"]),
            ]

            record_id = get_entry_id_or_create_it(
                db_cursor,
                "species",
                [("latin_name", row_data["latin_name"])],
                data=data,
            )
        db_connection.commit()
