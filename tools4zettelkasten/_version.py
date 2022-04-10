import os
import io


def read():
    """Read the version string from the VERSION text file
    and return the content as a string.
    Have a look at
    https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
    why we do this in such a complicated way. In summary: The version
    number has always to be read from the setuptools. When you do a clean
    install the dependencies are not installed yet. Then the _version.py script
    or the __init__.py script is not yet available, because the package
    is still in the process of installation. Therefor the setuptools need
    there own logic to read the version number. The easiest way is to do so
    is by configuring the VERSION file in the setup.cfg file."""
    with io.open(
        os.path.join(os.path.dirname(__file__), 'VERSION'), encoding="utf-8"
    ) as f:
        return f.read()


__version__ = read()
