class Error(Exception):
    """Base class for exceptions in this module."""

    pass


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
        self.message = "No Annoation file found for {}".format(
            audio_file,
        )
        super().__init__(self.message)