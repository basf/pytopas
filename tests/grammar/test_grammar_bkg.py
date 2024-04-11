"Test bkg"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_bkg = make_trivial_grammar_test(
    g.bkg,
    (
        "bkg 1",
        None,
        {
            "bkg": ast.BkgNode(
                [ast.ParameterNode(prm_value=ast.ParameterValueNode(Decimal(1)))]
            )
        },
    ),
    (
        "bkg @ 3391.558041 -1356.63652",
        [
            ast.BkgNode(
                params=[
                    ast.ParameterNode(
                        prm_to_be_refined=True,
                        prm_value=ast.ParameterValueNode(Decimal("3391.558041")),
                    ),
                    ast.ParameterNode(
                        prm_value=ast.ParameterValueNode(
                            Decimal("-1356.63652"),
                        ),
                    ),
                ]
            )
        ],
        None,
    ),
    (
        "bkg cheb  21.1707846`_0.182221081  0.554319881`_0.205423203",
        [
            ast.BkgNode(
                params=[
                    ast.ParameterNode(
                        prm_name=ast.ParameterNameNode(name="cheb"),
                        next=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(
                                value=Decimal("21.1707846"),
                                esd=Decimal("0.182221081"),
                                backtick=True,
                            ),
                            next=ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(
                                    value=Decimal("0.554319881"),
                                    esd=Decimal("0.205423203"),
                                    backtick=True,
                                ),
                            ),
                        ),
                    )
                ]
            )
        ],
        None,
    ),
)
