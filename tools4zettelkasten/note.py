from dataclasses import dataclass


@dataclass()
class Note:
    """A note
    standard filenames have the form of
    2_03_04a_5_Some_Topic_fb134b00b

    The correct form of the filenames is
    important for listing, reorganizing the
    Zettelkasten etc.
    """
    ordering: str
    """The ordering of the note"""
    base_filename: str
    """"The base of the filename"""
    id: str
    """The id of the note"""
