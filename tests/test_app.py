# test_app.py
from .context import tools4zettelkasten
import pytest


def test_app(capsys, example_fixture):
    # pylint: disable=W0612,W0613
    """Start command line interface without specifying
    a command. Help message will be displayed.

    Test is a bit complex because, click will end program
    with systemexit=0.
    So this exception has to be catched, otherwise
    test will fail.

    See
    https: // medium.com/python-pandemonium/
    testing-sys-exit-with-pytest-10c6e5f7726f
    for details

    ToDo:
    * assert exit code zero
    * assert help in message
    """
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        tools4zettelkasten.ZettelkastenTools.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0

    captured = capsys.readouterr()
    assert "--help" in captured.out
