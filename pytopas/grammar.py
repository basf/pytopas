"TOPAS grammar"
import pyparsing as pp
from pyparsing import (
    And,
    Forward,
    Group,
    White,
    Suppress,
    ZeroOrMore,
    DelimitedList,
    Word,
    Combine,
    SkipTo,
    Keyword,
    Opt,
    Literal,
    OneOrMore,
    QuotedString,
    ParseResults,
    Char,
    Regex,
    one_of,
    LineEnd,
)

EQUALS = Literal("=")
COLON = Literal(":")
SEMICOLON = Literal(";")
LPAR = Literal("(")
RPAR = Literal(")")

# forward declaration
prm_optional = Forward()
formula = Forward()
formula_el = Forward()

# comments
line_comment = Regex(r"'.*").set_name("line_comment")
block_comment = pp.c_style_comment


# strings
simple_str = Word(pp.printables)("simple_str")
ws_escaped_str = Combine(
    Word(pp.printables, exclude_chars="\\'")
    + OneOrMore(
        (Literal("\\").suppress() + White())
        + Opt(Word(pp.printables, exclude_chars="\\'"))
    ),
    adjacent=True,
)[1, ...]("ws_escaped_str")
quoted_str = pp.dbl_quoted_string("quoted_str")
string_val = (quoted_str | ws_escaped_str | simple_str)("string_val")


# simple numbers
integer = pp.common.integer("integer")
signed_integer = pp.common.signed_integer("signed_integer")
real = pp.common.real("real")
number = pp.common.number("number")

#
# Parameters
#

# The first character can be an upper or lower-case letter.
# Subsequent characters can include the underscore character '_'
# and the numbers 0 through 9.
parameter_name = Word(pp.alphas, pp.alphanums + "_")("parameter_name")

# The character ! placed before name signals that parameter is not to be refined
parameter_to_be_fixed = Literal("!")

# A parameter can also be flagged for refinement by placing
# the @ character at the start of its name
parameter_to_be_refined = Literal("@")

parameter_backtick = Literal("`")
parameter_min = Literal("_LIMIT_MIN_") + number("min_limit")
parameter_max = Literal("_LIMIT_MAX_") + number("max_limit")

# Like "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1"
parameter_value = Combine(
    number("value")
    + Opt(parameter_backtick)("backtick")
    + Opt("_" + number("esd"))
    + Opt(Opt(parameter_min) & Opt(parameter_max))
)("parameter_value").add_parse_action(lambda toks: ["".join(toks[0])])

# equations start with an equal sign and end in a semicolon
parameter_equation_reporting = (COLON + White()[...] + Literal("0"))(
    "parameter_equation_reporting"
)
parameter_equation = Combine(
    EQUALS.suppress()
    + formula
    + SEMICOLON.suppress()
    + Opt(White()[...] + parameter_equation_reporting).suppress()
)("parameter_equation")


# User defined parameters - the `prm` keyword
# [prm|local E]
# optionals: [min !E] [max !E] [del !E] [update !E] [stop_when !E] [val_on_continue !E]
prm_opts_val = parameter_value | parameter_equation
prm_min = (Keyword("min").suppress() + prm_opts_val)("prm_min")
prm_max = (Keyword("max").suppress() + prm_opts_val)("prm_max")
prm_del = (Keyword("del").suppress() + prm_opts_val)("prm_del")
prm_update = (Keyword("update").suppress() + prm_opts_val)("prm_update")
prm_stop_when = (Keyword("stop_when").suppress() + prm_opts_val)("prm_stop_when")
prm_val_on_continue = (Keyword("val_on_continue").suppress() + prm_opts_val)(
    "prm_val_on_continue"
)
prm_optional <<= (
    prm_min | prm_max | prm_del | prm_update | prm_stop_when | prm_val_on_continue
)
prm = Combine(
    Keyword("prm").suppress()
    + Opt(parameter_to_be_fixed)
    + Opt(parameter_name)
    + prm_opts_val
    + prm_optional[...]
)("prm")


#
# Formula
#


func_name = Word(pp.alphas, pp.alphanums + "_")("func_name")
func_arg = (formula[0, ...] | string_val)("func_arg")
func_args = Group(DelimitedList(func_arg))("func_args")
func_call = Combine(func_name + LPAR.suppress() + func_args + RPAR.suppress())(
    "func_call"
)

formula_el <<= (
    func_call
    | parameter_name[1, ...]
    | (parameter_to_be_refined + Opt(parameter_name) + Opt(formula_el))
    | (parameter_to_be_fixed + parameter_name + Opt(formula_el))
    | parameter_value + prm_optional[...]
    | parameter_equation + prm_optional[...]
    | prm_optional[1, ...]
)("formula_el")

formula <<= pp.helpers.infix_notation(
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
