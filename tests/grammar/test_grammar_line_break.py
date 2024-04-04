"Test line_break"

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_line_break = make_trivial_grammar_test(
    g.line_break,
    ("\n", None, {"line_break": ast.LineBreakNode()}),
    ("\r\n", None, {"line_break": ast.LineBreakNode()}),
    ("\r", None, {"line_break": ast.LineBreakNode()}),
    ("\t", None, {"line_break": ast.LineBreakNode()}),
)
