"Test FunctionCallNode"

import json
from pathlib import Path

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException

SIMPLE_DIR = Path(__file__).parent / "function_call"

ins = sorted(SIMPLE_DIR.glob("*.in.inp"))
jsons = sorted(SIMPLE_DIR.glob("*.json"))
outs = sorted(SIMPLE_DIR.glob("*.out.inp"))


@pytest.mark.parametrize(
    "in_path, json_path, out_path",
    zip(ins, jsons, outs),
)
def test_function_call_node(in_path: Path, json_path: Path, out_path: Path):
    "Test FunctionCallNode"
    text_in = in_path.read_text()[:-1]
    serialized = json.loads(json_path.read_text())
    text_out = out_path.read_text()[:-1]

    node = ast.FunctionCallNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.FunctionCallNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_function_call_node_unserialize_fail():
    "Test FunctionCallNode"
    with pytest.raises(ReconstructException):
        ast.FunctionCallNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.FunctionCallNode.unserialize(["not this node", 123])
