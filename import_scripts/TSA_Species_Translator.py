from mysql.connector.cursor import MySQLCursor
from tools.db.queries import get_id_of_entry_in_table


class TSA_Species_Translator:
    species_set = {}

    def __init__(self, db_cursor: MySQLCursor):
        db_cursor.execute(
            """
            SELECT 
            species_id, 
            tsa_to_ioc10_1 
            FROM species_synonyms 
            WHERE tsa_to_ioc10_1 is not null
            """
        )
        for row in db_cursor.fetchall():
            self.species_set[row[1]] = row[0]

    def get_species_id(
        self, db_cursor: MySQLCursor, latin_name: str, english_name: str
    ) -> int:
        species_id = get_id_of_entry_in_table(
            db_cursor, "species", [("latin_name", latin_name)]
        )
        if species_id is None:
            species_id = get_id_of_entry_in_table(
                db_cursor, "species", [("english_name", english_name)]
            )
            if species_id is None:
                try:
                    species_id = self.species_set[latin_name]
                except:
                    species_id = None
        return species_id