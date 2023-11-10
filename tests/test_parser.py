"Test TOPAS parser"

from dataclasses import asdict
import pytest

from pytopas.exc import ParseException, ParseWarning
from pytopas.base import FormulaNode
from pytopas.parser import RootNode


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "1 1",
            [
                "topas",
                ["formula", ["formula_element", 1]],
                ["formula", ["formula_element", 1]],
            ],
            "1 1",
        ),
    ],
)
def test_root_node(text_in: str, serialized, text_out):
    "Test RootNode"
    node = RootNode.parse(text_in, permissive=True)
    assert isinstance(node, RootNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
