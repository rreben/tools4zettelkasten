# test_app.py
from .context import zettelkasten_tools


def test_app(capsys, example_fixture):
    # pylint: disable=W0612,W0613
    zettelkasten_tools.ZettelkastenTools.run()
    captured = capsys.readouterr()

    assert "--help" in captured.out
