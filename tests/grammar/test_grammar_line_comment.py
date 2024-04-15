"Test line_comment"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_line_comment = make_trivial_grammar_test(g.line_comment, (" ' comment", [], {}))
