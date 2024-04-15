"Test local"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_local = make_trivial_grammar_test(
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
