"Test scale"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_scale = make_trivial_grammar_test(
    g.scale,
    (
        "scale 1",
        None,
        {
            "scale": ast.ScaleNode(
                ast.ParameterNode(prm_value=ast.ParameterValueNode(Decimal(1)))
            )
        },
    ),
    (
        "scale @  0.0224625979`",
        [
            ast.ScaleNode(
                param=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_value=ast.ParameterValueNode(
                        Decimal("0.0224625979"), backtick=True
                    ),
                ),
            )
        ],
        None,
    ),
    (
        "scale sc_2002698 0.001",
        [
            ast.ScaleNode(
                param=ast.ParameterNode(
                    prm_name=ast.ParameterNameNode(name="sc_2002698"),
                    prm_value=ast.ParameterValueNode(Decimal("0.001")),
                ),
            )
        ],
        None,
    ),
)
