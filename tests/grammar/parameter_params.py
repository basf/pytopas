"Common parameter's params"

from decimal import Decimal

from pytopas import ast

parameter_params = [
    (
        "min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@",
        [ast.ParameterNode(prm_to_be_refined=True)],
        {
            "parameter": ast.ParameterNode(prm_to_be_refined=True),
        },
    ),
    (
        "@ min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@ 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@ P_name",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_name=ast.ParameterNameNode("P_name"),
            ),
        ],
        None,
    ),
    (
        "@ P_name min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "@ P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_refined=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "! P_name",
        [
            ast.ParameterNode(
                prm_to_be_fixed=True,
                prm_name=ast.ParameterNameNode("P_name"),
            ),
        ],
        None,
    ),
    (
        "! P_name min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_fixed=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            )
        ],
        None,
    ),
    (
        "! P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_to_be_fixed=True,
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "P_name 0",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
            ),
        ],
        None,
    ),
    (
        "P_name 0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("P_name"),
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "P_name",
        [
            ast.ParameterNode(prm_name=ast.ParameterNameNode("P_name")),
        ],
        None,
    ),
    (
        "P_name min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("P_name"),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "0",
        [
            ast.ParameterNode(prm_value=ast.ParameterValueNode(value=Decimal(0))),
        ],
        None,
    ),
    (
        "0 min 1 max 2 del 3 update 4 stop_when 5 val_on_continue 6",
        [
            ast.ParameterNode(
                prm_value=ast.ParameterValueNode(value=Decimal(0)),
                prm_min=ast.ParameterValueNode(value=Decimal(1)),
                prm_max=ast.ParameterValueNode(value=Decimal(2)),
                prm_del=ast.ParameterValueNode(value=Decimal(3)),
                prm_update=ast.ParameterValueNode(value=Decimal(4)),
                prm_stop_when=ast.ParameterValueNode(value=Decimal(5)),
                prm_val_on_continue=ast.ParameterValueNode(value=Decimal(6)),
            ),
        ],
        None,
    ),
    (
        "= 0 ;",
        [
            ast.ParameterNode(
                prm_value=ast.ParameterEquationNode(
                    formula=ast.FormulaNode(
                        value=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(Decimal(0))
                        )
                    )
                )
            ),
        ],
        None,
    ),
    (
        "A1 B2 C3 D4",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("A1"),
                next=ast.ParameterNode(
                    prm_name=ast.ParameterNameNode("B2"),
                    next=ast.ParameterNode(
                        prm_name=ast.ParameterNameNode("C3"),
                        next=ast.ParameterNode(prm_name=ast.ParameterNameNode("D4")),
                    ),
                ),
            )
        ],
        None,
    ),
    (
        "A1 2 3 4",
        [
            ast.ParameterNode(
                prm_name=ast.ParameterNameNode("A1"),
                next=ast.ParameterNode(
                    prm_value=ast.ParameterValueNode(Decimal(2)),
                    next=ast.ParameterNode(
                        prm_value=ast.ParameterValueNode(Decimal(3)),
                        next=ast.ParameterNode(
                            prm_value=ast.ParameterValueNode(Decimal(4))
                        ),
                    ),
                ),
            )
        ],
        None,
    ),
]
