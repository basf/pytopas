"Test func_call"

from pytopas import grammar as g
from tests.grammar.func_call_params import func_call_params
from tests.helpers import make_trivial_grammar_test

test_func_call = make_trivial_grammar_test(g.func_call, *func_call_params)
