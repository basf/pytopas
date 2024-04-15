"Test block_comment"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_block_comment = make_trivial_grammar_test(
    g.block_comment, ("/* \n comment\n */", [], {})
)
