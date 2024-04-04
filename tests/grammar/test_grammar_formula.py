"Test formula"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.grammar.func_call_params import func_call_params
from tests.grammar.parameter_params import parameter_params
from tests.helpers import make_trivial_grammar_test

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

test_formula = make_trivial_grammar_test(
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
