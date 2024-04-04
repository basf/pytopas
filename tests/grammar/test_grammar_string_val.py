"Test string_val"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_string_val = make_trivial_grammar_test(
    g.string_val,
    (
        "string",
        None,
        {"string_val": "string", "simple_str": "string"},
    ),
    (
        "a\\ b",
        None,
        {"ws_escaped_str": "a b", "string_val": "a b"},
    ),
    ('"string"', None, {"quoted_str": "string", "string_val": "string"}),
    (
        '"string"',
        None,
        {"quoted_str": "string", "string_val": "string"},
    ),
)
