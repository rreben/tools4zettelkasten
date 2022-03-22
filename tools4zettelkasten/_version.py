import os
import io


def read():
    """Read a text file and return the content as a string."""
    with io.open(
        os.path.join(os.path.dirname(__file__), 'VERSION'), encoding="utf-8"
    ) as f:
        return f.read()


__version__ = read()
