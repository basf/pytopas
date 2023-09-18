"Test topas2json tree"
from contextlib import nullcontext as does_not_raise
from json import JSONDecodeError
from tempfile import NamedTemporaryFile

import pytest

from pytopas import TOPASParseTree, UnexpectedToken
from pytopas.cli import _json2topas_parse_args, json2topas


@pytest.mark.parametrize(
    "json_in, raises",
    [
        ('["topas", ["a = a + 1 ; 0"]]', does_not_raise()),
        ("...", pytest.raises(JSONDecodeError)),
        ('["topas", ["{}!@##}!@#"]]', pytest.raises(UnexpectedToken)),
    ],
)
def test_cli_json2topas(capsys, json_in: str, raises):
    "Test json2topas cli tool"

    with raises, NamedTemporaryFile() as tmp_file:
        tmp_file.write(json_in.encode("utf-8"))
        tmp_file.flush()

        args = _json2topas_parse_args([tmp_file.name])
        json2topas(args)

    captured = capsys.readouterr()

    with raises:
        tree = TOPASParseTree.from_json(json_in)
        assert captured.out == tree.to_topas() + "\n"
