"Test ParameterNameNode"


import pytest

from pytopas import ast
from pytopas.exc import ReconstructException


def test_parameter_name_node():
    "Test ParameterNameNode"
    text_in = "P_name1"
    node = ast.ParameterNameNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterNameNode)
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type, text_in]
    assert ast.ParameterNameNode.unserialize(serialized) == node


def test_parameter_name_node_unserialize_fail():
    "Test ParameterNameNode"
    with pytest.raises(ReconstructException):
        ast.ParameterNameNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.ParameterNameNode.unserialize(["not this node", 123])
    with pytest.raises(ReconstructException):
        ast.ParameterNameNode.unserialize(["parameter_name", 123])
