"Test root"
from decimal import Decimal

from pytopas import ast
from pytopas import grammar as g
from tests.helpers import make_trivial_grammar_test

test_root = make_trivial_grammar_test(
    g.root,
    (
        "1",
        [
            ast.RootNode(
                statements=[
                    ast.FormulaNode(
                        value=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(value=Decimal(1)),
                        )
                    )
                ]
            )
        ],
        None,
    ),
    (
        "prm 1",
        [
            ast.RootNode(
                statements=[
                    ast.PrmNode(
                        prm_value=ast.ParameterValueNode(value=Decimal(1)),
                    )
                ]
            )
        ],
        None,
    ),
    (
        "local a 1",
        [
            ast.RootNode(
                statements=[
                    ast.LocalNode(
                        ast.ParameterNode(
                            prm_name=ast.ParameterNameNode(name="a"),
                            prm_value=ast.ParameterValueNode(value=Decimal("1")),
                        )
                    )
                ]
            )
        ],
        None,
    ),
    (
        "existing_prm a *- 1;",
        [
            ast.RootNode(
                statements=[
                    ast.ExistingPrmNode(
                        name=ast.ParameterNameNode(name="a"),
                        op="*-",
                        modificator=ast.FormulaNode(
                            value=ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(Decimal("1")),
                            )
                        ),
                    )
                ]
            )
        ],
        None,
    ),
    (
        "num_runs 123",
        [ast.RootNode(statements=[ast.NumRunsNode(value=123)])],
        None,
    ),
    (
        "xdd filename",
        [ast.RootNode(statements=[ast.XddNode(filename="filename")])],
        None,
    ),
    (
        "axial_conv filament_length 1 sample_length 2 receiving_slit_length 3",
        [
            ast.RootNode(
                statements=[
                    ast.AxialConvNode(
                        filament_length=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(Decimal("1")),
                        ),
                        sample_length=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(Decimal("2")),
                        ),
                        receiving_slit_length=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(Decimal("3")),
                        ),
                    )
                ]
            )
        ],
        None,
    ),
    (
        "bkg 1",
        [
            ast.RootNode(
                statements=[
                    ast.BkgNode(
                        [
                            ast.ParameterNode(
                                prm_value=ast.ParameterValueNode(Decimal(1))
                            )
                        ]
                    )
                ]
            )
        ],
        None,
    ),
    (
        'macro name("arg1", "arg2") { "quoted string" }',
        [
            ast.RootNode(
                statements=[
                    ast.MacroNode(
                        name="name", args=["arg1", "arg2"], statements=["quoted string"]
                    )
                ]
            )
        ],
        None,
    ),
    (
        "\n",
        [ast.RootNode(statements=[ast.LineBreakNode()])],
        None,
    ),
    (
        "#@@!#$%^&*()",
        [ast.RootNode(statements=[ast.TextNode("#@@!#$%^&*()")])],
        None,
    ),
    (
        "#@@! #$% ^&*()",
        [ast.RootNode(statements=[ast.TextNode("#@@! #$% ^&*()")])],
        None,
    ),
)
