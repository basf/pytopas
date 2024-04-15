"Test integer"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_interger = make_trivial_grammar_test(g.integer, ("100", None, {"integer": 100}))
