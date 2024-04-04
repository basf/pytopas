"Test LineBreakNode"


from pytopas import ast


def test_line_break_node():
    "Test"
    text_in = "\n"
    node = ast.LineBreakNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.LineBreakNode)
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type]
    assert ast.LineBreakNode.unserialize(serialized) == node
