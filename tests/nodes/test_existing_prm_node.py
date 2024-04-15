"Test ExistingPrmNode"

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "existing_prm a ^= 1;",
            [
                "existing_prm",
                ["parameter_name", "a"],
                "^=",
                ["formula", ["p", {"v": ["parameter_value", "1"]}]],
            ],
            "existing_prm a ^= 1;",
        ),
    ],
)
def test_existing_prm_node(text_in: str, serialized, text_out):
    "Test ExistingPrmNode"
    node = ast.ExistingPrmNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ExistingPrmNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_existing_prm_unserialize_fail():
    "Test ExistingPrmNode"
    with pytest.raises(ReconstructException):
        ast.ExistingPrmNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.ExistingPrmNode.unserialize(["not this node", 1, 2, 3])
