"Test BkgNode"

import json
from pathlib import Path

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException

SIMPLE_DIR = Path(__file__).parent / "bkg"

ins = sorted(SIMPLE_DIR.glob("*.in.inp"))
jsons = sorted(SIMPLE_DIR.glob("*.json"))
outs = sorted(SIMPLE_DIR.glob("*.out.inp"))


@pytest.mark.parametrize(
    "in_path, json_path, out_path",
    zip(ins, jsons, outs),
)
def test_bkg_node(in_path: Path, json_path: Path, out_path: Path):
    "Test BkgNode"
    text_in = in_path.read_text()[:-1]
    serialized = json.loads(json_path.read_text())
    text_out = out_path.read_text()[:-1]

    node = ast.BkgNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.BkgNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_bkg_unserialize_fail():
    "Test BkgNode"
    with pytest.raises(ReconstructException):
        ast.BkgNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.BkgNode.unserialize(["not this node", 1])
    with pytest.raises(ReconstructException):
        ast.BkgNode.unserialize(["bkg"])
    with pytest.raises(ReconstructException):
        ast.BkgNode.unserialize(["bkg", [], "not dict"])
