"Test func_args"

from pytopas import grammar as g
from tests.grammar.func_args_params import func_args_params
from tests.helpers import make_trivial_grammar_test

test_func_args = make_trivial_grammar_test(g.func_args, *func_args_params)
