"Test xdd"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_xdd = make_trivial_grammar_test(
    g.xdd,
    (
        "xdd some/path/file.name",
        None,
        {"xdd": ast.XddNode(filename="some/path/file.name")},
    ),
    (
        'xdd "some/path/file.name"',
        [ast.XddNode(filename="some/path/file.name")],
        None,
    ),
    (
        'xdd "so me/pa th/file.name"',
        [ast.XddNode(filename="so me/pa th/file.name")],
        None,
    ),
    (
        "xdd { 0 1 2 }",
        [ast.XddNode(inline_data=[Decimal(0), Decimal(1), Decimal(2)])],
        None,
    ),
    (
        "xdd { _xy 0 1 2 }",
        [
            ast.XddNode(
                inline_data=[Decimal(0), Decimal(1), Decimal(2)], inline_data_xy=True
            )
        ],
        None,
    ),
    (
        "xdd filename range 1",
        [ast.XddNode(filename="filename", range=Decimal(1))],
        None,
    ),
    (
        "xdd filename range 1",
        [ast.XddNode(filename="filename", range=Decimal(1))],
        None,
    ),
    (
        "xdd filename xye_format gsas_format fullprof_format gui_reload gui_ignore",
        [
            ast.XddNode(
                filename="filename",
                xye_format=True,
                gsas_format=True,
                fullprof_format=True,
                gui_reload=True,
                gui_ignore=True,
            )
        ],
        None,
    ),
)
