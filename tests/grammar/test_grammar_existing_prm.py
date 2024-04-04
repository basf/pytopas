"Test local"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_existing_prm = make_trivial_grammar_test(
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
