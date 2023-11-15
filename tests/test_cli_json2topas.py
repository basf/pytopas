"Test topas2json tree"
import json
from contextlib import nullcontext as does_not_raise
from tempfile import NamedTemporaryFile

import pytest

from pytopas import TOPASParser
from pytopas.cli import _json2topas_parse_args, json2topas
from pytopas.exc import ReconstructException


@pytest.mark.parametrize(
    "json_in, raises",
    [
        ('["topas", ["fallback", "text"]]', does_not_raise()),
        ("...", pytest.raises(json.JSONDecodeError)),
        ('["topas", ["{}!@##}!@#"]]', pytest.raises(ReconstructException)),
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
        assert captured.out == TOPASParser.reconstruct(json.loads(json_in)) + "\n"
