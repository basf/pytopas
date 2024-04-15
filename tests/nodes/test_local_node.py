"Test LocalNode"

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "local a 1",
            [
                "local",
                ["p", {"n": ["parameter_name", "a"], "v": ["parameter_value", "1"]}],
            ],
            "local a 1",
        ),
        (
            "local a = 1;",
            [
                "local",
                [
                    "p",
                    {
                        "n": ["parameter_name", "a"],
                        "v": [
                            "prm_eq",
                            ["formula", ["p", {"v": ["parameter_value", "1"]}]],
                        ],
                    },
                ],
            ],
            "local a = 1;",
        ),
    ],
)
def test_local_node(text_in: str, serialized, text_out):
    "Test LocalNode and co"
    node = ast.LocalNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.LocalNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_local_unserialize_fail():
    "Test LocalNode"
    with pytest.raises(ReconstructException):
        ast.LocalNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.LocalNode.unserialize(["not this node", 1])
