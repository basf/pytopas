"Grammar tests"
import warnings
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pyparsing as pp
import pytest

from pytopas import ast
from pytopas import grammar as g
from pytopas.exc import ParseWarning


def d(elem: pp.ParserElement):  # pylint: disable=invalid-name
    "Enable debug"
    return elem.copy().set_debug(True)


def make_trivial_test(parser: pp.ParserElement, *params):
    "Create simple and dumb parametrized test"
    parser_debug = parser.copy().set_debug(True)

    @pytest.mark.parametrize("string, as_list, as_dict", params)
    def trivial_test(
        string: str,
        as_list: Optional[List[Any]],
        as_dict: Optional[Dict[str, Any]],
    ):
        "Trivial grammar tests"

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ParseWarning)
            results = parser_debug.copy().parse_string(string, parse_all=True)
        if as_list is not None:
            assert results.as_list() == as_list
        if as_dict is not None:
            assert results.as_dict() == as_dict

    return trivial_test


test_line_comment = make_trivial_test(g.line_comment, (" ' comment", [], {}))
test_block_comment = make_trivial_test(g.block_comment, ("/* \n comment\n */", [], {}))
test_interger = make_trivial_test(g.integer, ("100", None, {"integer": 100}))
test_signer_integer = make_trivial_test(
    g.signed_integer,
    ("100", None, {"signed_integer": 100}),
    ("+100", None, {"signed_integer": 100}),
    ("-100", None, {"signed_integer": -100}),
)
test_real = make_trivial_test(g.real, ("-1.23", None, {"real": Decimal("-1.23")}))
test_number = make_trivial_test(
    g.number,
    ("100", [Decimal(100)], {"number": Decimal(100)}),
    ("+100", [Decimal(100)], None),
    ("-1.23", [Decimal("-1.23")], None),
)

test_simple_str = make_trivial_test(
    g.simple_str, ("string", None, {"simple_str": "string"})
)
test_ws_escaped_str = make_trivial_test(
    g.ws_escaped_str, ("a\\ b", None, {"ws_escaped_str": "a b"})
)
test_quoted_str = make_trivial_test(
    g.quoted_str, ('"string"', None, {"quoted_str": "string"})
)
test_string_val = make_trivial_test(
    g.string_val,
    (
        "string",
        None,
        {"string_val": "string", "simple_str": "string"},
    ),
    (
        "a\\ b",
        None,
        {"ws_escaped_str": "a b", "string_val": "a b"},
    ),
    ('"string"', None, {"quoted_str": "string", "string_val": "string"}),
    (
        '"string"',
        None,
        {"quoted_str": "string", "string_val": "string"},
    ),
)

test_text = make_trivial_test(
    g.text,
    ("TEST", None, {"text": ast.TextNode(value="TEST")}),
)

test_line_break = make_trivial_test(
    g.line_break,
    ("\n", None, {"line_break": ast.LineBreakNode()}),
    ("\r\n", None, {"line_break": ast.LineBreakNode()}),
    ("\r", None, {"line_break": ast.LineBreakNode()}),
    ("\t", None, {"line_break": ast.LineBreakNode()}),
)

test_parameter_name = make_trivial_test(
    g.parameter_name,
    ("P_name", None, {"parameter_name": ast.ParameterNameNode(name="P_name")}),
)

test_parameter_value = make_trivial_test(
    g.parameter_value,
    ("1", None, {"parameter_value": ast.ParameterValueNode(value=Decimal(1))}),
    (
        "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
        None,
        {
            "parameter_value": ast.ParameterValueNode(
                value=Decimal("-12.3"),
                esd=Decimal("2"),
                backtick=True,
                lim_min=Decimal("-13"),
                lim_max=Decimal("2.1"),
            )
        },
    ),
)

test_parameter_equation = make_trivial_test(
    g.parameter_equation,
    (
        "= a + 1 ;",
        None,
        {
            "parameter_equation": ast.ParameterEquationNode(
                formula=ast.FormulaNode(
                    value=ast.FormulaAdd(
                        operands=[
                            ast.ParameterNode(prm_name=ast.ParameterNameNode(name="a")),
                            ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(value=Decimal(1)),
                            ),
                        ]
                    )
                ),
            )
        },
    ),
    (
        "= 1 + 2 ; : 123.123123",
        None,
        {
            "parameter_equation": ast.ParameterEquationNode(
                formula=ast.FormulaNode(
                    value=ast.FormulaAdd(
                        operands=[
                            ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(value=Decimal(1)),
                            ),
                            ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(value=Decimal(2)),
                            ),
                        ]
                    )
                ),
                reporting=ast.ParameterValueNode(value=Decimal("123.123123")),
            )
        },
    ),
    (
        "= sin() ; ",
        None,
        {
            "parameter_equation": ast.ParameterEquationNode(
                formula=ast.FormulaNode(value=ast.FunctionCallNode(name="sin")),
            ),
        },
    ),
)

parameter_params = [
    (
        "min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@",
        [ast.ParameterNode(prm_to_be_refined=True)],
        {
            "parameter": ast.ParameterNode(prm_to_be_refined=True),
        },
    ),
    (
        "@ min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@ 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@ P_name",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_name=ast.ParameterNameNode("P_name"),
            ),
        ],
        None,
    ),
    (
        "@ P_name min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@ P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "! P_name",
        [
            ast.ParameterNode(
                prm_to_be_fixed=True,
                prm_name=ast.ParameterNameNode("P_name"),
            ),
        ],
        None,
    ),
    (
        "! P_name min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_fixed=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "! P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_fixed=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "P_name 0",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
            ),
        ],
        None,
    ),
    (
        "P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "P_name",
        [
            ast.ParameterNode(prm_name=ast.ParameterNameNode("P_name")),
        ],
        None,
    ),
    (
        "P_name min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("P_name"),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "0",
        [
            ast.ParameterNode(prm_value=ast.ParameterValueNode(value=Decimal(0))),
        ],
        None,
    ),
    (
        "0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "= 0 ;",
        [
            ast.ParameterNode(
                prm_value=ast.ParameterEquationNode(
                    formula=ast.FormulaNode(
                        value=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(Decimal(0))
                        )
                    )
                )
            ),
        ],
        None,
    ),
    (
        "A1 B2 C3 D4",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("A1"),
                next=ast.ParameterNode(
                    prm_name=ast.ParameterNameNode("B2"),
                    next=ast.ParameterNode(
                        prm_name=ast.ParameterNameNode("C3"),
                        next=ast.ParameterNode(prm_name=ast.ParameterNameNode("D4")),
                    ),
                ),
            )
        ],
        None,
    ),
    (
        "A1 2 3 4",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("A1"),
                next=ast.ParameterNode(
                    prm_value=ast.ParameterValueNode(Decimal(2)),
                    next=ast.ParameterNode(
                        prm_value=ast.ParameterValueNode(Decimal(3)),
                        next=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(Decimal(4))
                        ),
                    ),
                ),
            )
        ],
        None,
    ),
]
test_parameter = make_trivial_test(g.parameter, *parameter_params)

test_prm = make_trivial_test(
    g.prm,
    (
        "prm 1",
        None,
        {"prm": ast.PrmNode(prm_value=ast.ParameterValueNode(value=Decimal(1)))},
    ),
    (
        (
            "prm ! P_name = a + 1; min 2 max =3; "
            "update 4 del =5; stop_when 6 val_on_continue 7"
        ),
        [
            ast.PrmNode(
                prm_to_be_fixed=True,
                prm_name=ast.ParameterNameNode(name="P_name"),
                prm_value=ast.ParameterEquationNode(
                    formula=ast.FormulaNode(
                        value=ast.FormulaAdd(
                            operands=[
                                ast.ParameterNode(
                                    prm_name=ast.ParameterNameNode(name="a"),
                                ),
                                ast.ParameterNode(
                                    prm_value=ast.ParameterValueNode(value=Decimal(1)),
                                ),
                            ]
                        )
                    ),
                ),
                prm_min=ast.ParameterValueNode(value=Decimal(2)),
                prm_max=ast.ParameterEquationNode(
                    formula=ast.FormulaNode(
                        value=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(value=Decimal(3))
                        )
                    )
                ),
                prm_del=ast.ParameterEquationNode(
                    formula=ast.FormulaNode(
                        value=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(value=Decimal(5))
                        )
                    )
                ),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(6)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(7)),
            ),
        ],
        None,
    ),
)


test_func_name = make_trivial_test(
    g.func_name, ("fun_ction", None, {"func_name": "fun_ction"})
)
func_args_params = [
    ("", [], {}),
    (",", [None, None], {}),
    ('"quoted string"', ["quoted string"], None),
    (
        "@",
        [
            ast.FormulaNode(value=ast.ParameterNode(prm_to_be_refined=True)),
        ],
        None,
    ),
    (
        ',"quoted string",min 1,@,@ min 1, @ P_name1, @ 1, @ P_name1 1,',
        [
            None,
            "quoted string",
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_min=ast.ParameterValueNode(value=Decimal(1))
                )
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(prm_to_be_refined=True),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_min=ast.ParameterValueNode(value=Decimal(1)),
                ),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_name=ast.ParameterNameNode(name="P_name1"),
                ),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_value=ast.ParameterValueNode(value=Decimal(1)),
                ),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_name=ast.ParameterNameNode(name="P_name1"),
                    prm_value=ast.ParameterValueNode(value=Decimal(1)),
                ),
            ),
            None,
        ],
        {},
    ),
    (
        "1/Cos(Th)",
        [
            ast.FormulaNode(
                value=ast.FormulaDiv(
                    operands=[
                        ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(value=Decimal(1))
                        ),
                        ast.FunctionCallNode(
                            name="Cos",
                            args=[
                                ast.FormulaNode(
                                    value=ast.ParameterNode(
                                        prm_name=ast.ParameterNameNode(name="Th")
                                    )
                                )
                            ],
                        ),
                    ]
                )
            )
        ],
        None,
    ),
]
test_func_args = make_trivial_test(g.func_args, *func_args_params)

func_call_params = list(
    map(
        lambda x: (
            f"FUN({x[0]})",
            [ast.FunctionCallNode(name="FUN", args=x[1])],
            None,
        ),
        func_args_params,
    )
)
test_func_call = make_trivial_test(g.func_call, *func_call_params)


formula_func_call_params = list(
    map(
        lambda x: (x[0], [ast.FormulaNode(value=x[1][0])], None),
        func_call_params,
    )
)
formula_parameter_params = list(
    map(
        lambda x: (x[0], [ast.FormulaNode(value=x[1][0])], None),
        parameter_params,
    )
)


_test_formula1_param_formula_div = ast.FormulaDiv(
    operands=[
        ast.FormulaMul(
            operands=[
                ast.FunctionCallNode(
                    name="a",
                    args=[
                        ast.FormulaNode(
                            value=ast.ParameterNode(
                                prm_name=ast.ParameterNameNode(name="b"),
                            )
                        ),
                        ast.FormulaNode(
                            value=ast.ParameterNode(
                                prm_name=ast.ParameterNameNode(name="c"),
                            )
                        ),
                    ],
                ),
                ast.ParameterNode(
                    prm_name=ast.ParameterNameNode(name="param"),
                ),
            ],
        ),
        ast.FormulaExp(
            operands=[
                ast.ParameterNode(
                    prm_to_be_fixed=True,
                    prm_name=ast.ParameterNameNode(name="param"),
                    prm_value=ast.ParameterValueNode(
                        value=Decimal(1),
                    ),
                ),
                ast.FormulaAdd(
                    operands=[
                        ast.ParameterNode(
                            prm_to_be_refined=True,
                            prm_name=ast.ParameterNameNode(name="param"),
                        ),
                        ast.FormulaSub(
                            operands=[
                                ast.ParameterNode(
                                    prm_value=ast.ParameterValueNode(value=Decimal(4)),
                                    prm_min=ast.ParameterValueNode(value=Decimal(2)),
                                ),
                                ast.ParameterNode(
                                    prm_name=None,
                                    prm_value=ast.ParameterValueNode(value=Decimal(5)),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

test_formula1 = make_trivial_test(
    g.formula,
    *formula_func_call_params,
    *formula_parameter_params,
    (
        (
            "a(b, c) * param / !param 1 ^ (@ param + 4 min 2 - 5) "
            "< 6 > 7 <= 9 >= b(c) == 1"
        ),
        [
            ast.FormulaNode(
                value=ast.FormulaGT(
                    operands=[
                        ast.FormulaGE(
                            operands=[
                                ast.FormulaLE(
                                    operands=[
                                        _test_formula1_param_formula_div,
                                        ast.ParameterNode(
                                            prm_value=ast.ParameterValueNode(
                                                value=Decimal(6)
                                            ),
                                        ),
                                    ],
                                ),
                                ast.FormulaLT(
                                    operands=[
                                        ast.ParameterNode(
                                            prm_to_be_fixed=False,
                                            prm_to_be_refined=False,
                                            prm_name=None,
                                            prm_value=ast.ParameterValueNode(
                                                value=Decimal(7),
                                            ),
                                        ),
                                        ast.ParameterNode(
                                            prm_value=ast.ParameterValueNode(
                                                value=Decimal(9)
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ast.FormulaEQ(
                            operands=[
                                ast.FunctionCallNode(
                                    name="b",
                                    args=[
                                        ast.FormulaNode(
                                            value=ast.ParameterNode(
                                                prm_name=ast.ParameterNameNode(name="c")
                                            )
                                        )
                                    ],
                                ),
                                ast.ParameterNode(
                                    prm_value=ast.ParameterValueNode(value=Decimal(1))
                                ),
                            ],
                        ),
                    ],
                )
            )
        ],
        None,
    ),
)

test_local = make_trivial_test(
    g.local,
    (
        "local a 1",
        None,
        {
            "local": ast.LocalNode(
                value=ast.ParameterNode(
                    prm_name=ast.ParameterNameNode("a"),
                    prm_value=ast.ParameterValueNode(Decimal(1)),
                )
            )
        },
    ),
    (
        "local a = 1;",
        [
            ast.LocalNode(
                value=ast.ParameterNode(
                    prm_name=ast.ParameterNameNode(name="a"),
                    prm_value=ast.ParameterEquationNode(
                        formula=ast.FormulaNode(
                            value=ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(Decimal("1")),
                            )
                        ),
                    ),
                )
            )
        ],
        None,
    ),
)


test_existing_prm = make_trivial_test(
    g.existing_prm,
    (
        "existing_prm a -= 1;",
        None,
        {
            "existing_prm": ast.ExistingPrmNode(
                name=ast.ParameterNameNode(name="a"),
                op="-=",
                modificator=ast.FormulaNode(
                    value=ast.ParameterNode(
                        prm_value=ast.ParameterValueNode(Decimal("1"))
                    )
                ),
            )
        },
    ),
)

test_num_runs = make_trivial_test(
    g.num_runs,
    ("num_runs 10", None, {"num_runs": ast.NumRunsNode(10)}),
)

test_root = make_trivial_test(
    g.root,
    (
        "1",
        [
            ast.RootNode(
                statements=[
                    ast.FormulaNode(
                        value=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(value=Decimal(1)),
                        )
                    )
                ]
            )
        ],
        None,
    ),
    (
        "prm 1",
        [
            ast.RootNode(
                statements=[
                    ast.PrmNode(
                        prm_value=ast.ParameterValueNode(value=Decimal(1)),
                    )
                ]
            )
        ],
        None,
    ),
    (
        "local a 1",
        [
            ast.RootNode(
                statements=[
                    ast.LocalNode(
                        ast.ParameterNode(
                            prm_name=ast.ParameterNameNode(name="a"),
                            prm_value=ast.ParameterValueNode(value=Decimal("1")),
                        )
                    )
                ]
            )
        ],
        None,
    ),
    (
        "existing_prm a *- 1;",
        [
            ast.RootNode(
                statements=[
                    ast.ExistingPrmNode(
                        name=ast.ParameterNameNode(name="a"),
                        op="*-",
                        modificator=ast.FormulaNode(
                            value=ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(Decimal("1")),
                            )
                        ),
                    )
                ]
            )
        ],
        None,
    ),
    (
        "num_runs 123",
        [ast.RootNode(statements=[ast.NumRunsNode(value=123)])],
        None,
    ),
    (
        "\n",
        [ast.RootNode(statements=[ast.LineBreakNode()])],
        None,
    ),
    (
        "#@@!#$%^&*()",
        [ast.RootNode(statements=[ast.TextNode("#@@!#$%^&*()")])],
        None,
    ),
    (
        "#@@! #$% ^&*()",
        [ast.RootNode(statements=[ast.TextNode("#@@! #$% ^&*()")])],
        None,
    ),
)
