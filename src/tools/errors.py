from typing import List, Tuple


class Error(Exception):
    """Base class for exceptions in this module."""


class ToManyAnnoationFilesError(Error):
    def __init__(self, audio_file: str, annotation_files: str) -> None:
        self.audio_file = audio_file
        self.annotation_files = annotation_files
        self.message = "To many Annoation files found for {}: {}".format(
            audio_file, annotation_files
        )
        super().__init__(self.message)


class NoAnnoationFileError(Error):
    def __init__(self, audio_file: str) -> None:
        self.audio_file = audio_file
        self.message = "No Annoation file found for {}.".format(
            audio_file,
        )
        super().__init__(self.message)


class EntryNotFoundInDbError(Error):
    def __init__(self, table: str, name: str) -> None:
        self.name = name
        self.message = "{name} found in table {table} of database.".format(
            name=name, table=table
        )
        super().__init__(self.message)


class MoreThanOneEntryInDbError(Error):
    def __init__(self, table: str, query: List[Tuple]) -> None:
        self.message = "{query} found not in table {table} of database.".format(
            query=query, table=table
        )
        super().__init__(self.message)
