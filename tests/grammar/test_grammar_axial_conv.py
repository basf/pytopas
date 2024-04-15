"Test axial_conv"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test


def mk_param_node_val(x: str):
    "Create ParameterNode with value"
    return ast.ParameterNode(
        prm_value=ast.ParameterValueNode(Decimal(x)),
    )


test_axial_conv = make_trivial_grammar_test(
    g.axial_conv,
    (
        ("axial_conv filament_length 1 sample_length 2 receiving_slit_length 3 "),
        None,
        {
            "axial_conv": ast.AxialConvNode(
                filament_length=mk_param_node_val("1"),
                sample_length=mk_param_node_val("2"),
                receiving_slit_length=mk_param_node_val("3"),
            )
        },
    ),
    (
        (
            "axial_conv filament_length 1 sample_length 2 receiving_slit_length 3 "
            "primary_soller_angle 4 secondary_soller_angle 5 axial_n_beta 6"
        ),
        None,
        {
            "axial_conv": ast.AxialConvNode(
                filament_length=mk_param_node_val("1"),
                sample_length=mk_param_node_val("2"),
                receiving_slit_length=mk_param_node_val("3"),
                primary_soller_angle=mk_param_node_val("4"),
                secondary_soller_angle=mk_param_node_val("5"),
                axial_n_beta=mk_param_node_val("6"),
            )
        },
    ),
)
