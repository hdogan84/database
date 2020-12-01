from pathlib import Path
from tools.configuration import parse_config
from tools.db import connectToDB, get_entry_id_or_create_it, get_id_of_entry_in_table

CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")

config = parse_config(CONFIG_FILE_PATH)

dog_to_ioc101 = (
    "do-g_to_ioc10.1",
    [
        ("Columba livia f. domestica", "Columba livia"),
        ("Zapornia parva", "Porzana parva"),
        ("Zapornia pusilla", "Porzana pusilla"),
    ],
)
tsa_to_ioc101 = (
    "tsa_to_ioc10.1",
    [
        ("Apus melba", "Tachymarptis melba"),
        ("Aquila pennata", "Hieraaetus pennatus"),
        ("Carduelis chloris'", "Chloris chloris "),
        ("Falco pelegrinoides", "Falco peregrinus"),
        ("Larus atricilla", "Leucophaeus atricilla"),
        ("Larus audouinii", "Ichthyaetus audouinii"),
        ("Larus genei", "Chroicocephalus genei"),
        ("Larus melanocephalus", "Ichthyaetus melanocephalus"),
        ("Larus pipixcan", "Leucophaeus pipixcan"),
        ("Larus ridibundus", "Chroicocephalus ridibundus"),
        ("Muscicapa latirostris", "Muscicapa dauurica"),
        ("Phalacrocorax pygmeus", "Microcarbo pygmaeus"),
        ("Regulus teneriffae", "Regulus regulus"),
        ("Serinus citrinella", "Carduelis citrinella"),
        ("Sterna bengalensis", "Thalasseus bengalensis"),
        ("Sterna sandvicensis", "Thalasseus sandvicensis"),
        ("Streptopelia senegalensis", "Spilopelia senegalensis"),
        ("Tetrao tetrix", "Lyrurus tetrix"),
    ],
)
not_matched = []
with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        for row_name, synonyms in [dog_to_ioc101, tsa_to_ioc101]:
            for synonym in synonyms:
                species_id = get_id_of_entry_in_table(
                    db_cursor, "species", [("latin_name", synonym[1])]
                )

                if species_id is None:
                    not_matched.append((row_name, synonym))
                    continue
                data = [("species_id", species_id), (row_name, synonym[0])]
                get_entry_id_or_create_it(db_cursor, "species_synonyms", data, data)
            db_connection.commit()

for i in not_matched:
    print(i)
print("not_matched: {}".format(len(not_matched)))
