"Test func_name"

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_func_name = make_trivial_grammar_test(
    g.func_name, ("fun_ction", None, {"func_name": "fun_ction"})
)
