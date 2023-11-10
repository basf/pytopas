"Trivial grammar tests"

from typing import Any, List, Dict, Optional

import pytest
from pyparsing import ParserElement
from pyparsing.results import ParseResults

from pytopas import trivial


def d(el: ParserElement):
    "Enable debug"
    return el.copy().set_debug(True)


test_comment_params = [
    (d(trivial.line_comment), " ' comment", [], {}),
    (d(trivial.block_comment), "/* \n comment\n */", [], {}),
]

test_numbers_params = [
    (d(trivial.integer), "100", [100], {"integer": 100}),
    (d(trivial.number), "100", [100], {"number": 100}),
    (d(trivial.signed_integer), "+100", [100], {"signed_integer": 100}),
    (d(trivial.number), "+100", [100], {"number": 100}),
    (d(trivial.real), "-1.23", [-1.23], {"real": -1.23}),
    (d(trivial.number), "-1.23", [-1.23], {"number": -1.23}),
]

test_str_params = [
    (d(trivial.simple_str), "string", ["string"], {"simple_str": "string"}),
    (
        d(trivial.string_val),
        "string",
        ["string"],
        {"simple_str": "string", "string_val": "string"},
    ),
    (d(trivial.ws_escaped_str), "a\\ b", ["a b"], {"ws_escaped_str": "a b"}),
    (
        d(trivial.string_val),
        "a\\ b",
        ["a b"],
        {"ws_escaped_str": "a b", "string_val": "a b"},
    ),
    (d(trivial.quoted_str), '"string"', ["string"], {"quoted_str": "string"}),
    (
        d(trivial.string_val),
        '"string"',
        ["string"],
        {"quoted_str": "string", "string_val": "string"},
    ),
]

test_parameter_params = [
    # TODO
    # (
    #     d(grammar.parameter_equation),
    #     "= a + 1 ; 1231.123",
    #     [["a+1"]],
    #     {"parameter_equation": "a+1"},
    # ),
]

# test_prm_params = [
#     (
#         grammar.prm.set_debug(True),
#         "prm a 1",
#         [["a 1"]],
#         {"prm": {"parameter_value": "1", "parameter_name": "a"}},
#     ),
#     (
#         grammar.prm.set_debug(True),
#         "prm !b2 = a + -0.10124`_0.01_LIMIT_MIN_0.1; min 0.1 max 5 del 1 update 1 stop_when 1 val_on_continue 1",
#         [["! b2 a+-0.10124`_0.01_LIMIT_MIN_0.1 0.1 5 1 1 1 1"]],
#         {
#             "prm": {
#                 "parameter_to_be_fixed": "!",
#                 "parameter_name": "b2",
#                 "parameter_equation": "a+-0.10124`_0.01_LIMIT_MIN_0.1",
#                 "prm_min": {"parameter_value": "0.1"},
#                 "prm_max": {"parameter_value": "5"},
#                 "prm_del": {"parameter_value": "1"},
#                 "prm_update": {"parameter_value": "1"},
#                 "prm_stop_when": {"parameter_value": "1"},
#                 "prm_val_on_continue": {"parameter_value": "1"},
#             }
#         },
#     ),
# ]
# retest with top level parser
# for params in test_prm_params.copy():
#     test_prm_params.append((grammar.TOPASParser.set_debug(True), *params[1:]))


test_formula_params = [
    # (d(grammar.func_name), "func", ["func"], {"func_name": "func"}),
    # (
    #     d(grammar.func_arg),
    #     '',
    #     [],
    #     {},
    # ),
    # (
    #     d(grammar.func_arg),
    #     '"str ing"',
    #     ["str ing"],
    #     {"func_arg": "str ing"},
    # ),
    # TODO
    # (
    #     d(grammar.func_arg),
    #     "name1 name2",
    #     [["name1 name2"]],
    #     {
    #         "func_arg": {
    #             "formula": "name1 name2",
    #         }
    #     },
    # ),
    # (
    #     d(grammar.func_args),
    #     "arg1, arg2,,, , a + 1, ",
    #     [], # TODO
    #     {},
    # ),
    # (
    #     grammar.func_args.set_debug(True),
    #     "arg1, arg2,,,, a + 1, ",
    #     None, #[["arg1"], ["arg2"], "", "", "", "a+1", ""],
    #     {},
    #     # {
    #     #     "func_args": [
    #     #         {"formula_el": ["arg1"], "parameter_name": "arg1"},
    #     #         {"formula_el": ["arg2"], "parameter_name": "arg2"},
    #     #         "",
    #     #         "",
    #     #         "",
    #     #         "a+1",
    #     #         "",
    #     #     ],
    #     #     "func_arg": "",
    #     # },
    # ),
    # (
    #     grammar.func_call.set_debug(True),
    #     "func()",
    #     [["func "]],
    #     {"func_call": {"func_name": "func", "func_args": [""], "func_arg": ""}},
    # ),
    # (
    #     grammar.func_call.set_debug(True),
    #     'func(a + 1 param_name, "string")',
    #     [['func a+1 param_name "string"']],
    #     {
    #         "func_call": {
    #             "func_name": "func",
    #             "func_args": [
    #                 {"formula_el": ["param_name"], "parameter_name": "param_name"},
    #                 {"quoted_str": '"string"'},
    #             ],
    #             "func_arg": {"quoted_str": '"string"'},
    #         },
    #     },
    # ),
    # (
    #     grammar.formula.set_debug(True),
    #     "a(b, c) * param / !param 1 ^ (@ param + 4 min 2 - 5) < 6 > 7 <= 9 >= b(a) == 1",
    #     [
    #         [
    #             [
    #                 ["a b c"],
    #                 "*",
    #                 "param",
    #                 "/",
    #                 "!",
    #                 "param",
    #                 "1",
    #                 "^",
    #                 ["@", "param", "+", "4", ["2"], "-", "5"],
    #             ],
    #             "<",
    #             "6",
    #             ">",
    #             "7",
    #             "<=",
    #             "9",
    #             ">=",
    #             ["b a"],
    #             "==",
    #             "1",
    #         ]
    #     ],
    #     None,
    # ),
]


@pytest.mark.parametrize(
    "parser, string, as_list, as_dict",
    [
        *test_comment_params,
        *test_numbers_params,
        *test_str_params,
    ],
)
def test_trivial(
    parser: ParserElement,
    string: str,
    as_list: Optional[List[Any]],
    as_dict: Optional[Dict[str, Any]],
):
    "Trivial grammar tests"

    results = parser.parse_string(string)
    if as_list is not None:
        assert results.as_list() == as_list
    if as_dict is not None:
        assert results.as_dict() == as_dict

        recovered = ParseResults.from_dict(as_dict)
        assert recovered.as_dict() == results.as_dict()
