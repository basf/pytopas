"Test prm"

from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_prm = make_trivial_grammar_test(
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
