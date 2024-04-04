"Test parameter_equation"

from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_parameter_equation = make_trivial_grammar_test(
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
