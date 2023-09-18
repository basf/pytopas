"Test topas2json tree"
from contextlib import nullcontext as does_not_raise
from tempfile import NamedTemporaryFile

import pytest

from pytopas import TOPASParser, UnexpectedToken
from pytopas.cli import _topas2json_parse_args, topas2json


@pytest.mark.parametrize(
    "topas_in, compact, raises",
    [
        ("a = a + 1 ; 0", False, does_not_raise()),
        ("a = a + 1 ; 0", True, does_not_raise()),
        ("{}!@##}!@#", True, pytest.raises(UnexpectedToken)),
    ],
)
def test_cli_topas2json(capsys, topas_in, compact, raises):
    "Test topas2json cli tool"

    with raises, NamedTemporaryFile() as tmp_file:
        tmp_file.write(topas_in.encode("utf-8"))
        tmp_file.flush()

        args = _topas2json_parse_args(
            ["-c", tmp_file.name] if compact else [tmp_file.name]
        )
        topas2json(args)

    captured = capsys.readouterr()

    with raises:
        tree = TOPASParser().parse(topas_in)
        assert captured.out == tree.to_json(compact=compact) + "\n"
