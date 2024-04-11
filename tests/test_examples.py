"Examples tests"
import warnings
from pathlib import Path
from typing import Optional

import pytest

from pytopas import TOPASParser, ast
from pytopas.exc import ParseWarning


@pytest.mark.parametrize(
    "file_name, fallbacks",
    [
        ("2002698.str", 2),
        ("4115474.str", 1),
        ("determine_dI.INP", 13),
        ("diffpy_example.INP", 22),
        ("Disordered_configuration_analysis.INP", 74),
        ("dmitrienka-sucrose-new.INP", 79),
        ("LightForm-group-adc_040_7Nb_TDload_725C_15mms_00000.inp", 65),
        ("mylist.txt", 3),
        ("NCM-Doped-stoe-29082022.INP", 48),
        ("Raw_XY_converter.INP", 9),
        ("starting_R_lebail.INP", 22),
        ("y2mn2o7-selectivity-1_65.INP", 34),
    ],
)
def test_examples(file_name: str, fallbacks: Optional[int]):
    "Test examples"
    text_cls = ast.DepsMixin.text_cls
    fallback_parser = text_cls.get_parser()
    file_path = Path(__file__).parent.parent / "examples" / file_name

    assert file_path.exists()
    fallback_counter = 0
    orig_debug_actions = fallback_parser.debugActions

    def action(*args):
        nonlocal fallback_counter
        fallback_counter += 1
        sup = orig_debug_actions.debug_match
        if sup:
            sup(*args)

    fallback_parser.set_debug_actions(
        start_action=orig_debug_actions.debug_try,  # type: ignore
        success_action=action,
        exception_action=orig_debug_actions.debug_fail,  # type: ignore
    )

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ParseWarning)
        TOPASParser.parse(file_path.read_text())

    if fallbacks is not None:
        assert fallbacks == fallback_counter
    fallback_parser.debugActions = orig_debug_actions
