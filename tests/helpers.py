"Some test helpers"

import warnings
from typing import Any, Dict, List, Optional

import pyparsing as pp
import pytest

from pytopas.exc import ParseWarning


def enable_pe_debug(elem: pp.ParserElement):
    "Enable debug"
    return elem.copy().set_debug(True)


def make_trivial_grammar_test(parser: pp.ParserElement, *params):
    "Create simple and dumb parametrized grammar test"
    parser_debug = parser.copy().set_debug(True)

    @pytest.mark.parametrize("string, as_list, as_dict", params)
    def trivial_test(
        string: str,
        as_list: Optional[List[Any]],
        as_dict: Optional[Dict[str, Any]],
    ):
        "Trivial grammar tests"

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ParseWarning)
            results = parser_debug.copy().parse_string(string, parse_all=True)
            print(results)
        if as_list is not None:
            assert results.as_list() == as_list
        if as_dict is not None:
            assert results.as_dict() == as_dict

    return trivial_test
