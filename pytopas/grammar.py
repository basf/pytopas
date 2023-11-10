"TOPAS grammar"
import pyparsing as pp
from pyparsing import (
    Forward,
    Group,
    DelimitedList,
    Word,
    Combine,
    Keyword,
    Opt,
    Literal,
    one_of,
    Empty,
)
from pyparsing.results import ParseResults

from .trivial import (
    EQUALS,
    COLON,
    SEMICOLON,
    LPAR,
    RPAR,
    line_comment,
    block_comment,
    quoted_str,
    number,
)
from .basis import ParameterNameNode, ParameterValueNode

pp.ParserElement.enablePackrat()


# forward declaration
prm_optional = Forward()
formula = Forward()
formula_el = Forward()


# The character ! placed before name signals that parameter is not to be refined
parameter_to_be_fixed = Literal("!").set_results_name("parameter_to_be_fixed")

# A parameter can also be flagged for refinement by placing
# the @ character at the start of its name
parameter_to_be_refined = Literal("@").set_results_name("parameter_to_be_refined")

parameter_name = ParameterNameNode.get_parser()
parameter_value = ParameterValueNode.get_parser()


# equations start with an equal sign and end in a semicolon


def parameter_equation_action(toks: ParseResults):
    "Format parameter equation"

    tok = toks[0]
    if not isinstance(tok, ParseResults):
        return
    print(tok.dump())
    print(list(tok.values()))

    print(tok.get("formula", "no formula"))

    return ParseResults.from_dict(
        {
            "parameter_equation": {
                "formula": toks[0],
                "reporting": None,
            }
        }
    )


parameter_equation_reporting = (COLON + number)("parameter_equation_reporting")
parameter_equation = (
    (
        EQUALS.suppress()
        + formula
        + SEMICOLON.suppress()
        + Opt(parameter_equation_reporting)
        # adjacent=False,
        # join_string=" ",
    )
    .add_parse_action(parameter_equation_action)
    .set_results_name("parameter_equation")
)


# User defined parameters - the `prm` keyword
# [prm|local E]
# optionals: [min !E] [max !E] [del !E] [update !E] [stop_when !E] [val_on_continue !E]
prm_opts_val = parameter_value | parameter_equation
prm_min = Combine(Keyword("min").suppress() + prm_opts_val, adjacent=False)("prm_min")
prm_max = Combine(Keyword("max").suppress() + prm_opts_val, adjacent=False)("prm_max")
prm_del = Combine(Keyword("del").suppress() + prm_opts_val, adjacent=False)("prm_del")
prm_update = Combine(Keyword("update").suppress() + prm_opts_val, adjacent=False)(
    "prm_update"
)
prm_stop_when = Combine(Keyword("stop_when").suppress() + prm_opts_val, adjacent=False)(
    "prm_stop_when"
)
prm_val_on_continue = Combine(
    Keyword("val_on_continue").suppress() + prm_opts_val, adjacent=False
)("prm_val_on_continue")
prm_optional <<= (
    prm_min | prm_max | prm_del | prm_update | prm_stop_when | prm_val_on_continue
)
prm = Combine(
    Keyword("prm").suppress()
    + Opt(parameter_to_be_fixed)
    + Opt(parameter_name)
    + prm_opts_val
    + prm_optional[...],
    adjacent=False,
    join_string=" ",
)("prm")


#
# Formula
#


def debug_action(s: str, loc: int, toks: ParseResults):
    "help me"
    print(s)


func_name = Word(pp.alphas, pp.alphanums + "_").set_results_name("func_name")
func_arg = (
    (formula | quoted_str | Empty()).add_parse_action(debug_action)
    # .add_parse_action(lambda toks: tok or '' for tok in toks[0])
    .set_results_name("func_arg")
)
func_args = (
    DelimitedList(func_arg, allow_trailing_delim=True)
    # .add_parse_action(lambda toks: ParseResults.from_dict({"func_args": toks.get("func_args")}))
    .set_results_name("func_args")
)
func_call = Combine(
    func_name + LPAR + Group(Opt(func_args)) + RPAR,
    adjacent=False,
    join_string="",
)("func_call")

formula_el <<= (
    func_call
    | parameter_name[1, ...]
    | (parameter_to_be_refined + Opt(parameter_name) + Opt(formula_el))
    | (parameter_to_be_fixed + parameter_name + Opt(formula_el))
    | parameter_value + prm_optional[...]
    | parameter_equation + prm_optional[...]
    | prm_optional[1, ...]
).set_results_name("formula_el")


formula <<= (
    pp.helpers.infix_notation(
        formula_el,
        [
            ("-", 1, pp.helpers.OpAssoc.RIGHT),
            (one_of("* / ^"), 2, pp.helpers.OpAssoc.LEFT),
            (one_of("+ -"), 2, pp.helpers.OpAssoc.LEFT),
            (one_of("== < <= > >="), 2, pp.helpers.opAssoc.LEFT),
        ],
        lpar=LPAR.suppress(),
        rpar=RPAR.suppress(),
    )
    .set_results_name("formula")
)

# The local keyword is used for defining named parameters
# as local to the top, xdd or phase level
local = Combine(
    Keyword("local").suppress()
    + parameter_name
    + (parameter_value | parameter_equation)
)("local")


# [existing_prm E]...
# Allowed operators for existing_prm are +=, -=, *-, /= and ^=
EXISTING_PRM_OPERATOR = one_of("+= -= *- /= ^= =")("existing_prm_operator")
existing_prm = Combine(
    Literal("existing_prm").suppress()
    + parameter_name
    + EXISTING_PRM_OPERATOR.suppress()
    + formula
    + SEMICOLON.suppress()
    + Opt(parameter_equation_reporting).suppress()
)("existing_prm")


pp.autoname_elements()
TOPASParser = (prm | local | existing_prm | formula)[...]
TOPASParser.ignore(line_comment)
TOPASParser.ignore(block_comment)
