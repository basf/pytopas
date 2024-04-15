"Test LineBreakNode"

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException


def test_line_break_node():
    "Test LineBreakNode"
    text_in = "\n"
    node = ast.LineBreakNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.LineBreakNode)
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type]
    assert ast.LineBreakNode.unserialize(serialized) == node


def test_line_break_node_unserialize_fail():
    "Test LineBreakNode"
    with pytest.raises(ReconstructException):
        ast.LineBreakNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.LineBreakNode.unserialize(["not line break"])
