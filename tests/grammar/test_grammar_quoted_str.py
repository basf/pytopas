"Test quoted_str"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_quoted_str = make_trivial_grammar_test(
    g.quoted_str, ('"string"', None, {"quoted_str": "string"})
)
