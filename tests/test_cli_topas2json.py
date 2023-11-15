"Test topas2json tree"
import json
from contextlib import nullcontext as does_not_raise
from tempfile import NamedTemporaryFile

import pytest

from pytopas.cli import _topas2json_parse_args, topas2json
from pytopas.parser import Parser
from pytopas.exc import ParseException, ParseWarning


@pytest.mark.parametrize(
    "topas_in, permissive, warns",
    [
        ("1", False, does_not_raise()),
        ("!@#$%^&*()", True, pytest.warns()),
        ("!@#$%^&*()", False, pytest.warns()),
    ],
)
def test_cli_topas2json(capsys, topas_in, permissive, warns):
    "Test topas2json cli tool"

    with NamedTemporaryFile() as tmp_file:
        tmp_file.write(topas_in.encode("utf-8"))
        tmp_file.flush()

        args = _topas2json_parse_args(
            ["-p", tmp_file.name] if permissive else [tmp_file.name]
        )

        with warns:
            topas2json(args)

    captured = capsys.readouterr()

    with warns:
        text = Parser.parse(topas_in, permissive)
        assert captured.out == json.dumps(text) + "\n"
