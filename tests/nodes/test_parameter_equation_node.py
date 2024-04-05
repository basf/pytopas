"Test ParameterEquationNode"

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "= a + 1 ;",
            [
                "prm_eq",
                [
                    "formula",
                    [
                        "+",
                        ["p", {"n": ["parameter_name", "a"]}],
                        ["p", {"v": ["parameter_value", "1"]}],
                    ],
                ],
            ],
            "= a + 1;",
        ),
        (
            "= 1 + 2 ; : 123.123123",
            [
                "prm_eq",
                [
                    "formula",
                    [
                        "+",
                        ["p", {"v": ["parameter_value", "1"]}],
                        ["p", {"v": ["parameter_value", "2"]}],
                    ],
                ],
                ["parameter_value", "123.123123"],
            ],
            "= 1 + 2; : 123.123123",
        ),
        (
            "= fun() ;",
            ["prm_eq", ["formula", ["func_call", "fun"]]],
            "= fun();",
        ),
    ],
)
def test_parameter_equation_node(text_in: str, serialized, text_out):
    "Test ParameterEquationNode"
    node = ast.ParameterEquationNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterEquationNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_parameter_equation_node_unserialize_fail():
    "Test ParameterEquationNode"
    with pytest.raises(ReconstructException):
        ast.ParameterEquationNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.ParameterEquationNode.unserialize(["not this node", 123])
