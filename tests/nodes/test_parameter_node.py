"Test ParameterNode"

import json
from pathlib import Path

import pytest

from pytopas import ast

SIMPLE_DIR = Path(__file__).parent / "parameter_node"

ins = sorted(SIMPLE_DIR.glob("*.in.inp"))
jsons = sorted(SIMPLE_DIR.glob("*.json"))
outs = sorted(SIMPLE_DIR.glob("*.out.inp"))


@pytest.mark.parametrize(
    "in_path, json_path, out_path",
    zip(ins, jsons, outs),
)
def test_axial_conv_node(in_path: Path, json_path: Path, out_path: Path):
    "Test ParameterNode"
    text_in = in_path.read_text()[:-1]
    serialized = json.loads(json_path.read_text())
    text_out = out_path.read_text()[:-1]

    node = ast.ParameterNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
