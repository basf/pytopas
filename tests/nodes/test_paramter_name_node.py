"Test ParameterNameNode"


from pytopas import ast

def test_parameter_name_node():
    "Test ParameterNameNode"
    text_in = "P_name1"
    node = ast.ParameterNameNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterNameNode)
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type, text_in]
    assert ast.ParameterNameNode.unserialize(serialized) == node
