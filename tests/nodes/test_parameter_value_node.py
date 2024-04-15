"Test ParameterValueName"

from dataclasses import asdict
from decimal import Decimal

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException


@pytest.mark.parametrize(
    "text_in, as_dict, text_out",
    [
        (
            "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
            {
                "value": Decimal("-12.3"),
                "esd": 2,
                "backtick": True,
                "lim_min": Decimal(-13),
                "lim_max": Decimal("2.1"),
            },
            "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
        ),
        (
            "10_LIMIT_MAX_20_LIMIT_MIN_5",
            {
                "value": 10,
                "esd": None,
                "backtick": False,
                "lim_min": 5,
                "lim_max": 20,
            },
            "10_LIMIT_MIN_5_LIMIT_MAX_20",
        ),
    ],
)
def test_parameter_value_node(text_in, as_dict, text_out):
    "Test ParameterValueNode"
    node = ast.ParameterValueNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.ParameterValueNode)
    assert asdict(node) == as_dict
    assert node.unparse() == text_out
    serialized = node.serialize()
    assert serialized == [node.type, text_out]
    assert ast.ParameterValueNode.unserialize(serialized) == node


def test_parameter_name_node_unserialize_fail():
    "Test ParameterValueNode"
    with pytest.raises(ReconstructException):
        ast.ParameterValueNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.ParameterValueNode.unserialize(["not this node", 123])
    with pytest.raises(ReconstructException):
        ast.ParameterValueNode.unserialize(["parameter_value", 123])
