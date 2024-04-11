"Test local"
from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_num_runs = make_trivial_grammar_test(
    g.num_runs,
    ("num_runs 10", None, {"num_runs": ast.NumRunsNode(10)}),
    (
        "num_runs runs",
        None,
        {"num_runs": ast.NumRunsNode(ast.ParameterNameNode(name="runs"))},
    ),
)
