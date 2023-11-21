"Test topas2json tree"
import json
import warnings
from contextlib import nullcontext as does_not_raise
from tempfile import NamedTemporaryFile

import pytest

from pytopas.cli import _topas2json_parse_args, topas2json
from pytopas.exc import ParseWarning
from pytopas.parser import Parser


@pytest.mark.parametrize(
    "topas_in, ignore_warnings, warns",
    [
        ("1", False, does_not_raise()),
        ("!@#$%^&*()", False, pytest.warns(ParseWarning)),
        ("!@#$%^&*()", True, does_not_raise()),
    ],
)
def test_cli_topas2json(capsys, topas_in, ignore_warnings, warns):
    "Test topas2json cli tool"

    with NamedTemporaryFile() as tmp_file:
        tmp_file.write(topas_in.encode("utf-8"))
        tmp_file.flush()

        args = _topas2json_parse_args(
            ["--ignore-warnings", tmp_file.name] if ignore_warnings else [tmp_file.name]
        )

        with warns:
            topas2json(args)

    captured = capsys.readouterr()

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ParseWarning)
        text = Parser.parse(topas_in)
        assert captured.out == json.dumps(text) + "\n"
