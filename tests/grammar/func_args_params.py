"Common func args"

from decimal import Decimal

from pytopas import ast

func_args_params = [
    ("", [], {}),
    (",", [None, None], {}),
    ('"quoted string"', ["quoted string"], None),
    (
        "@",
        [
            ast.FormulaNode(value=ast.ParameterNode(prm_to_be_refined=True)),
        ],
        None,
    ),
    (
        ',"quoted string",min 1,@,@ min 1, @ P_name1, @ 1, @ P_name1 1,',
        [
            None,
            "quoted string",
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_min=ast.ParameterValueNode(value=Decimal(1))
                )
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(prm_to_be_refined=True),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_min=ast.ParameterValueNode(value=Decimal(1)),
                ),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_name=ast.ParameterNameNode(name="P_name1"),
                ),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_value=ast.ParameterValueNode(value=Decimal(1)),
                ),
            ),
            ast.FormulaNode(
                value=ast.ParameterNode(
                    prm_to_be_refined=True,
                    prm_name=ast.ParameterNameNode(name="P_name1"),
                    prm_value=ast.ParameterValueNode(value=Decimal(1)),
                ),
            ),
            None,
        ],
        {},
    ),
    (
        "1/Cos(Th)",
        [
            ast.FormulaNode(
                value=ast.FormulaDiv(
                    operands=[
                        ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(value=Decimal(1))
                        ),
                        ast.FunctionCallNode(
                            name="Cos",
                            args=[
                                ast.FormulaNode(
                                    value=ast.ParameterNode(
                                        prm_name=ast.ParameterNameNode(name="Th")
                                    )
                                )
                            ],
                        ),
                    ]
                )
            )
        ],
        None,
    ),
]
