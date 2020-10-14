QUERY_FIND_ENTRY_IN_TABLE_BY_NAME = """
SELECT id FROM {table} WHERE name = '{name}';
"""
QUERY_INSERT_PERSON = """
INSERT INTO person (name) VALUES ('{name}')
"""
QUERY_INSERT_EQUIPMENT = """
INSERT INTO equipment (name, sound_device, microphone, remarks) VALUES ('{name}','{sound_device}','{microphone}','{remarks}')
"""
