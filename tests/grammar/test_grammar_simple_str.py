"Test ws_escaped_str"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_ws_escaped_str = make_trivial_grammar_test(
    g.ws_escaped_str, ("a\\ b", None, {"ws_escaped_str": "a b"})
)
