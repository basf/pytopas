"Test TextNode"

import pytest

from pytopas import ast
from pytopas.exc import ParseWarning


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
