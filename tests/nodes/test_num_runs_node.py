"Test NumRunsNode"

import pytest

from pytopas import ast

@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "num_runs 10",
            ["num_runs", 10],
            "num_runs 10",
        ),
    ],
)
def test_num_runs_node(text_in: str, serialized, text_out):
    "Test NumRunsNode and co"
    node = ast.NumRunsNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.NumRunsNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
