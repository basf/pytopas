"Test text"

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_text = make_trivial_grammar_test(
    g.text,
    ("TEST", None, {"text": ast.TextNode(value="TEST")}),
)
