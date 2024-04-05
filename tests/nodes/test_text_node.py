"Test TextNode"

import pytest

from pytopas import ast
from pytopas.exc import ParseWarning, ReconstructException


def test_text_node():
    "Test TextNode"
    text = "some random text"
    with pytest.warns(ParseWarning):
        node = ast.TextNode.parse(text)
    assert node
    assert node.value == text.split(" ", maxsplit=1)[0]
    assert node.unparse() == text.split(" ", maxsplit=1)[0]
    serialized = node.serialize()
    assert serialized == [node.type, text.split(" ", maxsplit=1)[0]]
    assert ast.TextNode.unserialize(serialized) == node

    with pytest.warns(ParseWarning):
        text_node = ast.ParameterValueNode.parse(text)
    assert isinstance(text_node, ast.TextNode)
    assert text_node == node


def test_text_node_dump(capsys):
    "Test TextNode"
    text = "some random text"
    with pytest.warns(ParseWarning):
        ast.TextNode.parse(text, print_dump=True)
    captured = capsys.readouterr()
    assert "TextNode" in captured.out


def test_text_node_match_unserialize_fail():
    "Test TextNode"
    with pytest.raises(ReconstructException):
        ast.TextNode.match_unserialize((ast.TextNode,), [])


def test_text_node_unserialize_fail():
    "Test TextNode"
    with pytest.raises(ReconstructException):
        ast.TextNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.TextNode.unserialize(["not text node", "text"])
    with pytest.raises(ReconstructException):
        ast.TextNode.unserialize(["text", [1, 2, 3]])
