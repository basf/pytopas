"Common func_call's params"

from pytopas import ast
from tests.grammar.func_args_params import func_args_params

func_call_params = list(
    map(
        lambda x: (
            f"FUN({x[0]})",
            [ast.FunctionCallNode(name="FUN", args=x[1])],
            None,
        ),
        func_args_params,
    )
)
