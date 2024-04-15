"Test parameter_value"

from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_parameter_value = make_trivial_grammar_test(
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
