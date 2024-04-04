"Test PrmNode"

import pytest

from pytopas import ast

@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "prm !P_name =0; min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
            [
                "prm",
                {
                    "!": True,
                    "n": ["parameter_name", "P_name"],
                    "v": [
                        "prm_eq",
                        ["formula", ["p", {"v": ["parameter_value", "0"]}]],
                    ],
                    "_": ["parameter_value", "1"],
                    "^": ["parameter_value", "2"],
                    "d": ["parameter_value", "3"],
                    "u": ["parameter_value", "4"],
                    "s": ["parameter_value", "5"],
                    "c": ["parameter_value", "6"],
                },
            ],
            (
                "prm ! P_name = 0; min 1 max 2 del 3 "
                "update 4 stop_when 5 val_on_continue 6"
            ),
        ),
    ],
)
def test_prm_node(text_in: str, serialized, text_out):
    "Test PrmNode and co"
    node = ast.PrmNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.PrmNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
