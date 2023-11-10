"Test base nodes"

from dataclasses import asdict
import pytest

from pytopas.exc import ParseException, ParseWarning
from pytopas.base import (
    FallbackNode,
    ParameterNameNode,
    ParameterValueNode,
    FormulaNode,
)


def test_fallback_node():
    "Test FallbackNode"
    text = "some random text"
    node = FallbackNode.parse(text)
    assert node.value == text
    assert node.unparse() == text
    serialized = node.serialize()
    assert serialized == [node.type, text]
    assert FallbackNode.unserialize(serialized) == node

    with pytest.warns(ParseWarning):
        fallback_node = ParameterValueNode.parse(text)
        assert isinstance(fallback_node, FallbackNode)
    assert fallback_node == node

    with pytest.raises(ParseException):
        ParameterValueNode.parse(text, permissive=False)


def test_parameter_name_node():
    "Test ParameterNameNode"
    text_in = "P_name1"
    node = ParameterNameNode.parse(text_in, permissive=False)
    assert isinstance(node, ParameterNameNode)
    assert asdict(node) == {"name": text_in}
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type, text_in]
    assert ParameterNameNode.unserialize(serialized) == node


@pytest.mark.parametrize(
    "text_in, as_dict, text_out",
    [
        (
            "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
            {
                "value": -12.3,
                "esd": 2,
                "backtick": True,
                "lim_min": -13,
                "lim_max": 2.1,
            },
            "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
        ),
        (
            "10_LIMIT_MAX_20_LIMIT_MIN_5",
            {
                "value": 10,
                "esd": None,
                "backtick": False,
                "lim_min": 5,
                "lim_max": 20,
            },
            "10_LIMIT_MIN_5_LIMIT_MAX_20",
        ),
    ],
)
def test_parameter_value_node(text_in, as_dict, text_out):
    "Test ParameterValueNode"
    node = ParameterValueNode.parse(text_in, permissive=False)
    assert isinstance(node, ParameterValueNode)
    assert asdict(node) == as_dict
    assert node.unparse() == text_out
    serialized = node.serialize()
    assert serialized == [node.type, text_out]
    assert ParameterValueNode.unserialize(serialized) == node


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        # test different elements
        (
            "1",
            ["formula", ["formula_element", 1]],
            "1",
        ),
        # arith operations
        (
            "+ 1",
            ["formula", ["formula_element", 1]],
            "1",
        ),
        (
            "- 1",
            ["formula", ["formula_element", -1]],
            "-1",
        ),
        (
            "1+2+3+4",
            [
                "formula",
                [
                    "+",
                    ["formula_element", 1],
                    ["formula_element", 2],
                    ["formula_element", 3],
                    ["formula_element", 4],
                ],
            ],
            "1 + 2 + 3 + 4",
        ),
        (
            "1-2-3-4",
            [
                "formula",
                [
                    "-",
                    ["formula_element", 1],
                    ["formula_element", 2],
                    ["formula_element", 3],
                    ["formula_element", 4],
                ],
            ],
            "1 - 2 - 3 - 4",
        ),
        (
            "1*2*3*4",
            [
                "formula",
                [
                    "*",
                    ["formula_element", 1],
                    ["formula_element", 2],
                    ["formula_element", 3],
                    ["formula_element", 4],
                ],
            ],
            "1 * 2 * 3 * 4",
        ),
        (
            "1/2/3/4",
            [
                "formula",
                [
                    "/",
                    ["formula_element", 1],
                    ["formula_element", 2],
                    ["formula_element", 3],
                    ["formula_element", 4],
                ],
            ],
            "1 / 2 / 3 / 4",
        ),
        (
            "1^2^3^4",
            [
                "formula",
                [
                    "^",
                    ["formula_element", 1],
                    ["formula_element", 2],
                    ["formula_element", 3],
                    ["formula_element", 4],
                ],
            ],
            "1 ^ 2 ^ 3 ^ 4",
        ),
        (
            "1+(2-3)*4/5^(6+7)",
            [
                "formula",
                [
                    "+",
                    ["formula_element", 1],
                    [
                        "/",
                        [
                            "*",
                            ["-", ["formula_element", 2], ["formula_element", 3]],
                            ["formula_element", 4],
                        ],
                        [
                            "^",
                            ["formula_element", 5],
                            ["+", ["formula_element", 6], ["formula_element", 7]],
                        ],
                    ],
                ],
            ],
            "1 + ( 2 - 3 ) * 4 / 5 ^ ( 6 + 7 )",
        ),
        # comparison operations
        (
            "1==1",
            ["formula", ["==", ["formula_element", 1], ["formula_element", 1]]],
            "1 == 1",
        ),
        (
            "1!=1",
            ["formula", ["!=", ["formula_element", 1], ["formula_element", 1]]],
            "1 != 1",
        ),
        (
            "1<1",
            ["formula", ["<", ["formula_element", 1], ["formula_element", 1]]],
            "1 < 1",
        ),
        (
            "1<=1",
            ["formula", ["<=", ["formula_element", 1], ["formula_element", 1]]],
            "1 <= 1",
        ),
        (
            "1>1",
            ["formula", [">", ["formula_element", 1], ["formula_element", 1]]],
            "1 > 1",
        ),
        (
            "1>=1",
            ["formula", [">=", ["formula_element", 1], ["formula_element", 1]]],
            "1 >= 1",
        ),
    ],
)
def test_formula_node(text_in: str, serialized, text_out):
    "Test FormulaNode and co"
    node = FormulaNode.parse(text_in, permissive=False)
    assert isinstance(node, FormulaNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
