"Test RootNode"

import json
from contextlib import nullcontext
from itertools import chain
from pathlib import Path

import pytest

from pytopas import ast
from pytopas.exc import ParseWarning

SIMPLE_DIR = Path(__file__).parent / "root"
WARN_DIR = Path(__file__).parent / "root_warn"

params = []
for dir in [SIMPLE_DIR, WARN_DIR]:
    ins = list(sorted(dir.glob("*.in.inp")))
    jsons = sorted(dir.glob("*.json"))
    outs = sorted(dir.glob("*.out.inp"))
    warns = nullcontext()
    if dir == WARN_DIR:
        warns = pytest.warns(ParseWarning)
    params = chain(params, zip(ins, jsons, outs, len(ins) * [warns]))


@pytest.mark.parametrize("in_path, json_path, out_path, warns", params)
def test_root_node(in_path: Path, json_path: Path, out_path: Path, warns):
    "Test RootNode and co"
    text_in = in_path.read_text()
    serialized = json.loads(json_path.read_text())
    text_out = out_path.read_text()
    with warns:
        node = ast.RootNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.RootNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
