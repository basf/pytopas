"Test base nodes"

from contextlib import nullcontext
from dataclasses import asdict
from decimal import Decimal

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


def test_parameter_name_node():
    "Test ParameterNameNode"
    text_in = "P_name1"
    node = ast.ParameterNameNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterNameNode)
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type, text_in]
    assert ast.ParameterNameNode.unserialize(serialized) == node


def test_line_break_node():
    "Test"
    text_in = "\n"
    node = ast.LineBreakNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.LineBreakNode)
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type]
    assert ast.LineBreakNode.unserialize(serialized) == node


@pytest.mark.parametrize(
    "text_in, as_dict, text_out",
    [
        (
            "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
            {
                "value": Decimal("-12.3"),
                "esd": 2,
                "backtick": True,
                "lim_min": Decimal(-13),
                "lim_max": Decimal("2.1"),
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
    node = ast.ParameterValueNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterValueNode)
    assert asdict(node) == as_dict
    assert node.unparse() == text_out
    serialized = node.serialize()
    assert serialized == [node.type, text_out]
    assert ast.ParameterValueNode.unserialize(serialized) == node


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
    "Test ParameterEquationNode and co"
    node = ast.ParameterEquationNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterEquationNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "@ P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
            [
                "p",
                {
                    "@": True,
                    "n": ["parameter_name", "P_name"],
                    "v": ["parameter_value", "0"],
                    "_": ["parameter_value", "1"],
                    "^": ["parameter_value", "2"],
                    "d": ["parameter_value", "3"],
                    "u": ["parameter_value", "4"],
                    "s": ["parameter_value", "5"],
                    "c": ["parameter_value", "6"],
                },
            ],
            "@ P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        ),
        (
            "! P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
            [
                "p",
                {
                    "!": True,
                    "n": ["parameter_name", "P_name"],
                    "v": ["parameter_value", "0"],
                    "_": ["parameter_value", "1"],
                    "^": ["parameter_value", "2"],
                    "d": ["parameter_value", "3"],
                    "u": ["parameter_value", "4"],
                    "s": ["parameter_value", "5"],
                    "c": ["parameter_value", "6"],
                },
            ],
            "! P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        ),
        (
            "A1 B2 C3 D4",
            [
                "p",
                {
                    "n": ["parameter_name", "A1"],
                    ">": [
                        "p",
                        {
                            "n": ["parameter_name", "B2"],
                            ">": [
                                "p",
                                {
                                    "n": ["parameter_name", "C3"],
                                    ">": ["p", {"n": ["parameter_name", "D4"]}],
                                },
                            ],
                        },
                    ],
                },
            ],
            "A1 B2 C3 D4",
        ),
    ],
)
def test_parameter_node(text_in: str, serialized, text_out):
    "Test ParameterNode and co"
    node = ast.ParameterNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "prm !P_name =0; min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
            [
                "prm",
                {
                    "!": True,
                    "n": ["parameter_name", "P_name"],
                    "v": [
                        "prm_eq",
                        ["formula", ["p", {"v": ["parameter_value", "0"]}]],
                    ],
                    "_": ["parameter_value", "1"],
                    "^": ["parameter_value", "2"],
                    "d": ["parameter_value", "3"],
                    "u": ["parameter_value", "4"],
                    "s": ["parameter_value", "5"],
                    "c": ["parameter_value", "6"],
                },
            ],
            (
                "prm ! P_name = 0; min 1 max 2 del 3 "
                "update 4 stop_when 5 val_on_continue 6"
            ),
        ),
    ],
)
def test_prm_node(text_in: str, serialized, text_out):
    "Test PrmNode and co"
    node = ast.PrmNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.PrmNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            (
                'FUN(,"quoted string",min 1,@,@ min 1, '
                "@ P_name1, @ 1, @ P_name1 1,1/Cos(Th),)"
            ),
            [
                "func_call",
                "FUN",
                None,
                "quoted string",
                ["formula", ["p", {"_": ["parameter_value", "1"]}]],
                ["formula", ["p", {"@": True}]],
                ["formula", ["p", {"@": True, "_": ["parameter_value", "1"]}]],
                ["formula", ["p", {"@": True, "n": ["parameter_name", "P_name1"]}]],
                ["formula", ["p", {"@": True, "v": ["parameter_value", "1"]}]],
                [
                    "formula",
                    [
                        "p",
                        {
                            "@": True,
                            "n": ["parameter_name", "P_name1"],
                            "v": ["parameter_value", "1"],
                        },
                    ],
                ],
                [
                    "formula",
                    [
                        "/",
                        ["p", {"v": ["parameter_value", "1"]}],
                        [
                            "func_call",
                            "Cos",
                            ["formula", ["p", {"n": ["parameter_name", "Th"]}]],
                        ],
                    ],
                ],
                None,
            ],
            (
                'FUN(, "quoted string", min 1, @, @ min 1, '
                "@ P_name1, @ 1, @ P_name1 1, 1 / Cos(Th), )"
            ),
        ),
    ],
)
def test_func_call_node(text_in: str, serialized, text_out):
    "Test FuncionCallNode and co"
    node = ast.FunctionCallNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.FunctionCallNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@pytest.mark.parametrize(
    "cls_in, cls_out, text_in, serialized, text_out",
    [
        (
            ast.FormulaUnaryPlus,
            ast.ParameterNode,
            "+ 1",
            ["p", {"v": ["parameter_value", "1"]}],
            "1",
        ),
        (
            ast.FormulaUnaryMinus,
            ast.FormulaUnaryMinus,
            "- 1",
            ["-1", ["p", {"v": ["parameter_value", "1"]}]],
            "- 1",
        ),
        (
            ast.FormulaAdd,
            ast.FormulaAdd,
            "1 + 1",
            [
                "+",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 + 1",
        ),
        (
            ast.FormulaSub,
            ast.FormulaSub,
            "1 - 1",
            [
                "-",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 - 1",
        ),
        (
            ast.FormulaMul,
            ast.FormulaMul,
            "1 * 1",
            [
                "*",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 * 1",
        ),
        (
            ast.FormulaDiv,
            ast.FormulaDiv,
            "1 / 1",
            [
                "/",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 / 1",
        ),
        (
            ast.FormulaExp,
            ast.FormulaExp,
            "1 ^ 1",
            [
                "^",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 ^ 1",
        ),
        (
            ast.FormulaEQ,
            ast.FormulaEQ,
            "1 == 1",
            [
                "==",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 == 1",
        ),
        (
            ast.FormulaNE,
            ast.FormulaNE,
            "1 != 1",
            [
                "!=",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 != 1",
        ),
        (
            ast.FormulaLE,
            ast.FormulaLE,
            "1 < 1",
            [
                "<",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 < 1",
        ),
        (
            ast.FormulaLT,
            ast.FormulaLT,
            "1 <= 1",
            [
                "<=",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 <= 1",
        ),
        (
            ast.FormulaGE,
            ast.FormulaGE,
            "1 > 1",
            [
                ">",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 > 1",
        ),
        (
            ast.FormulaGT,
            ast.FormulaGT,
            "1 >= 1",
            [
                ">=",
                ["p", {"v": ["parameter_value", "1"]}],
                ["p", {"v": ["parameter_value", "1"]}],
            ],
            "1 >= 1",
        ),
    ],
)
def test_formula_op_nodes(cls_in, cls_out, text_in: str, serialized, text_out):
    "Test FormulaOp and co"
    node = cls_in.parse(text_in, parse_all=True)
    assert isinstance(node, cls_out)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "TEST+(TEST-TEST)*TEST/TEST^(TEST+TEST)",
            [
                "formula",
                [
                    "+",
                    ["p", {"n": ["parameter_name", "TEST"]}],
                    [
                        "/",
                        [
                            "*",
                            [
                                "-",
                                ["p", {"n": ["parameter_name", "TEST"]}],
                                ["p", {"n": ["parameter_name", "TEST"]}],
                            ],
                            ["p", {"n": ["parameter_name", "TEST"]}],
                        ],
                        [
                            "^",
                            ["p", {"n": ["parameter_name", "TEST"]}],
                            [
                                "+",
                                ["p", {"n": ["parameter_name", "TEST"]}],
                                ["p", {"n": ["parameter_name", "TEST"]}],
                            ],
                        ],
                    ],
                ],
            ],
            "TEST + ( TEST - TEST ) * TEST / TEST ^ ( TEST + TEST )",
        ),
        (
            "1+(2-3)*4/5^(6+7)",
            [
                "formula",
                [
                    "+",
                    ["p", {"v": ["parameter_value", "1"]}],
                    [
                        "/",
                        [
                            "*",
                            [
                                "-",
                                ["p", {"v": ["parameter_value", "2"]}],
                                ["p", {"v": ["parameter_value", "3"]}],
                            ],
                            ["p", {"v": ["parameter_value", "4"]}],
                        ],
                        [
                            "^",
                            ["p", {"v": ["parameter_value", "5"]}],
                            [
                                "+",
                                ["p", {"v": ["parameter_value", "6"]}],
                                ["p", {"v": ["parameter_value", "7"]}],
                            ],
                        ],
                    ],
                ],
            ],
            "1 + ( 2 - 3 ) * 4 / 5 ^ ( 6 + 7 )",
        ),
    ],
)
def test_formula_node(text_in: str, serialized, text_out):
    "Test FormulaNode and co"
    node = ast.FormulaNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.FormulaNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@pytest.mark.parametrize(
    "text_in, serialized, text_out, warns",
    [
        (
            "\n",
            ["topas", ["lb"]],
            "\n",
            nullcontext(),
        ),
        (
            "!#^%&^%^&@#%&^@%#",
            ["topas", ["text", "!#^%&^%^&@#%&^@%#"]],
            "!#^%&^%^&@#%&^@%#",
            pytest.warns(ParseWarning),
        ),
        (
            "a(b,c)",
            [
                "topas",
                [
                    "formula",
                    [
                        "func_call",
                        "a",
                        ["formula", ["p", {"n": ["parameter_name", "b"]}]],
                        ["formula", ["p", {"n": ["parameter_name", "c"]}]],
                    ],
                ],
            ],
            "a(b, c)",
            nullcontext(),
        ),
        (
            "prm ! P_name1 123",
            [
                "topas",
                [
                    "prm",
                    {
                        "!": True,
                        "n": ["parameter_name", "P_name1"],
                        "v": ["parameter_value", "123"],
                    },
                ],
            ],
            "prm ! P_name1 123",
            nullcontext(),
        ),
    ],
)
def test_root_node(text_in: str, serialized, text_out, warns):
    "Test RootNode and co"
    with warns:
        node = ast.RootNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.RootNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
