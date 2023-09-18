"Trivial grammar tests"

from typing import Any

import pytest

from pytopas import TOPASParser, TOPASParseTree


@pytest.mark.parametrize(
    "topas_in, obj_out, topas_out, compact",
    [
        # NAME / PARAMETER_NAME
        (
            "some_name",
            ("formula", [("NAME", "some_name")]),
            "some_name",
            False,
        ),
        ("some_name", "some_name", "some_name", True),
        # other
        ("1", ("formula", [("parameter_value", [("PARAMETER_VAL", "1")])]), "1", False),
        ("1", "1", "1", True),
    ],
)
def test_trivial(topas_in: str, obj_out: Any, topas_out: str, compact: bool):
    "Trivial grammar tests"
    parser = TOPASParser()

    tree = parser.parse(topas_in)
    serialized = tree.serialize(compact=compact)
    assert serialized == ("topas", [obj_out])

    restored_tree = TOPASParseTree.from_tuples(serialized)
    assert restored_tree == tree

    restored_src = restored_tree.to_topas()
    assert restored_src == topas_out
