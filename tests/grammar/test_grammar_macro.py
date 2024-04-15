"Test macro"

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_grammar_macro = make_trivial_grammar_test(
    g.macro,
    ("macro name { }", None, {"macro": ast.MacroNode(name="name")}),
    (
        "macro name {}",
        [ast.MacroNode(name="name")],
        None,
    ),
    (
        "macro name{}",
        [ast.MacroNode(name="name")],
        None,
    ),
    (
        "macro name { num_runs 10 }",
        [ast.MacroNode(name="name", statements=[ast.NumRunsNode(10)])],
        None,
    ),
    (
        "macro name {num_runs 10}",
        [ast.MacroNode(name="name", statements=[ast.NumRunsNode(10)])],
        None,
    ),
    (
        'macro name { "quoted string" }',
        [ast.MacroNode(name="name", statements=["quoted string"])],
        None,
    ),
    (
        'macro name {"quoted string"}',
        [ast.MacroNode(name="name", statements=["quoted string"])],
        None,
    ),
    (
        'macro name("arg") {}',
        [ast.MacroNode(name="name", args=["arg"])],
        None,
    ),
    (
        'macro name("arg1", "arg2") {}',
        [ast.MacroNode(name="name", args=["arg1", "arg2"])],
        None,
    ),
)
