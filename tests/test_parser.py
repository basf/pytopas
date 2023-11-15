"Test TOPAS parser"

import pytest
from pytopas.exc import ParseWarning
from pytopas.base import DepsMixin
from pytopas.parser import RootNode, Parser

from tests.test_base import DummyTestNode


class DepsOverrideMixin(DepsMixin):
    @classmethod
    @property
    def formula_cls(cls):
        return DummyTestNode


class RootNodeTest(RootNode, DepsOverrideMixin):
    pass


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "TEST TEST PANIC\nTEST\nPANIC",
            [
                "topas",
                ["test"],
                ["test"],
                ["fallback", "PANIC"],
                ["test"],
                ["fallback", "PANIC"],
            ],
            "TEST TEST PANIC TEST PANIC",
        ),
    ],
)
def test_root_node(text_in: str, serialized, text_out):
    "Test RootNode"
    with pytest.warns(ParseWarning):
        node = RootNodeTest.parse(text_in, permissive=True)
    assert isinstance(node, RootNodeTest)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_parser():
    "Test Parser"
    serialized = Parser.parse("1")
    assert serialized == ["topas", ["formula", ["formula_element", 1]]]
    src = Parser.reconstruct(serialized)
    assert src == "1"
