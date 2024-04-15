"Test parameter"

from pytopas import grammar as g
from tests.grammar.parameter_params import parameter_params
from tests.helpers import make_trivial_grammar_test

test_parameter = make_trivial_grammar_test(g.parameter, *parameter_params)
