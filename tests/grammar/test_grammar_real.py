"Test real"

from decimal import Decimal

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_real = make_trivial_grammar_test(
    g.real, ("-1.23", None, {"real": Decimal("-1.23")})
)
