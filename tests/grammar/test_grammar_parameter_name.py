"Test parameter_name"

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_parameter_name = make_trivial_grammar_test(
    g.parameter_name,
    ("P_name", None, {"parameter_name": ast.ParameterNameNode(name="P_name")}),
)
