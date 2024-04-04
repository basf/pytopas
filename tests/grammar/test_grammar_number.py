"Test number"

from decimal import Decimal

from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_number = make_trivial_grammar_test(
    g.number,
    ("100", [Decimal(100)], {"number": Decimal(100)}),
    ("+100", [Decimal(100)], None),
    ("-1.23", [Decimal("-1.23")], None),
)
