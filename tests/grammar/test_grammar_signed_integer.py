"Test signed_integer"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_signed_integer = make_trivial_grammar_test(
    g.signed_integer,
    ("100", None, {"signed_integer": 100}),
    ("+100", None, {"signed_integer": 100}),
    ("-100", None, {"signed_integer": -100}),
)
