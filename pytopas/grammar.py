"Trivial grammar"
from decimal import Decimal
from typing import Type

import pyparsing as pp

from . import ast

# NOTE: packrat is not working!
pp.ParserElement.enable_left_recursion()


def toks_pop_action(toks: pp.ParseResults):
    "Take first element action"
    return toks[0]


EQUALS = pp.Literal("=")
COLON = pp.Literal(":")
SEMICOLON = pp.Literal(";")
LPAR = pp.Literal("(")
RPAR = pp.Literal(")")


# comments
line_comment = pp.Regex(r"'.*")("line_comment").suppress()
block_comment = pp.c_style_comment("block_comment").suppress()


# simple numbers
integer = pp.common.integer("integer")
signed_integer = pp.common.signed_integer("signed_integer")
real = pp.common.real("real").set_parse_action(pp.token_map(Decimal))
number = (real | signed_integer)("number").set_parse_action(pp.token_map(Decimal))


#
# strings
#


def quoted_str_action(toks: pp.ParseResults):
    "Undoublequote string action"
    tok = toks[0]
    result = (
        tok.strip('"')
        if isinstance(tok, str) and tok.startswith('"') and tok.endswith('"')
        else tok
    )
    return result


simple_str = pp.Word(pp.printables)("simple_str")
ws_escaped_str = pp.Combine(
    pp.Word(pp.printables, exclude_chars="\\'")
    + (
        pp.Literal("\\").suppress()
        + pp.White()
        + pp.Opt(pp.Word(pp.printables, exclude_chars="\\'"))
    )[1, ...],
    adjacent=True,
)("ws_escaped_str")
quoted_str = pp.dbl_quoted_string("quoted_str").add_parse_action(quoted_str_action)
string_val = (quoted_str | ws_escaped_str | simple_str)("string_val")

#
# text
#
text = (
    pp.Regex(r"\S+")
    .set_results_name("text")
    .add_parse_action(ast.TextNode.parse_action)
)

#
# line break
#
line_break = pp.LineEnd()("line_break").add_parse_action(ast.LineBreakNode.parse_action)

#
# forward declarations
#
formula = pp.Forward()


#
# Parameters
#


# The first character can be an upper or lower-case letter.
# Subsequent characters can include the underscore character '_'
# and the numbers 0 through 9.
parameter_name = pp.Word(pp.alphas, pp.alphanums + "_")(
    "parameter_name"
).add_parse_action(ast.ParameterNameNode.parse_action)


# The character ! placed before name signals that parameter is not to be refined
parameter_to_be_fixed = pp.Literal("!")("parameter_to_be_fixed").add_parse_action(
    lambda toks: toks[0] == "!"
)
# A parameter can also be flagged for refinement by placing
# the @ character at the start of its name
parameter_to_be_refined = pp.Literal("@")("parameter_to_be_refined").add_parse_action(
    lambda toks: toks[0] == "@"
)


parameter_backtick = pp.Literal("`")("parameter_backtick").add_parse_action(
    lambda toks: toks[0] == "`"
)
parameter_lim_min = pp.Literal("_LIMIT_MIN_").suppress() + number("parameter_lim_min")
parameter_lim_max = pp.Literal("_LIMIT_MAX_").suppress() + number("parameter_lim_max")
parameter_value = pp.Combine(
    number("value")
    + pp.Opt(parameter_backtick)("backtick")
    + pp.Opt("_" + number("esd"))
    + pp.Opt(
        pp.Opt(parameter_lim_min)("lim_min") & pp.Opt(parameter_lim_max)("lim_max")
    ),
    adjacent=True,
    join_string="",
)("parameter_value").add_parse_action(ast.ParameterValueNode.parse_action)

# equations start with an equal sign and end in a semicolon
parameter_equation = (
    EQUALS.suppress()
    + formula("formula")
    + SEMICOLON.suppress()
    + pp.Opt(COLON.suppress() + parameter_value("reporting"))
)("parameter_equation").add_parse_action(ast.ParameterEquationNode.parse_action)


# User defined parameters - the `prm` keyword
# [prm|local E]
# optionals: [min !E] [max !E] [del !E] [update !E] [stop_when !E] [val_on_continue !E]
prm_opts_val = (parameter_value | parameter_equation).add_parse_action(toks_pop_action)
prm_min = pp.Keyword("min").suppress() + prm_opts_val("prm_min")
prm_max = pp.Keyword("max").suppress() + prm_opts_val("prm_max")
prm_del = pp.Keyword("del").suppress() + prm_opts_val("prm_del")
prm_update = pp.Keyword("update").suppress() + prm_opts_val("prm_update")
prm_stop_when = pp.Keyword("stop_when").suppress() + prm_opts_val("prm_stop_when")
prm_val_on_continue = pp.Keyword("val_on_continue").suppress() + prm_opts_val(
    "prm_val_on_continue"
)
parameter_optional = (
    prm_min | prm_max | prm_del | prm_update | prm_stop_when | prm_val_on_continue
)


parameter = (
    parameter_optional[1, ...]
    | (
        (parameter_to_be_refined("prm_to_be_refined") + parameter_optional[1, ...])
        | (
            parameter_to_be_refined("prm_to_be_refined")
            + pp.Opt(
                prm_opts_val("prm_value")
                ^ (parameter_name("prm_name") + pp.Opt(prm_opts_val("prm_value")))
            )
            + parameter_optional[...]
        )
        | (
            parameter_to_be_fixed("prm_to_be_fixed")
            + parameter_name("prm_name")
            + pp.Opt(prm_opts_val("prm_value"))
            + parameter_optional[...]
        )
        | (
            parameter_name("prm_name")
            + prm_opts_val("prm_value")
            + parameter_optional[...]
        )
        | parameter_name("prm_name") + parameter_optional[...]
        | prm_opts_val("prm_value") + parameter_optional[...]
    )
    ^ pp.Group(parameter_name + (parameter_name | parameter_value)[1, ...])
)("parameter").add_parse_action(ast.ParameterNode.parse_action)
prm = (
    pp.Keyword("prm").suppress()
    + pp.Opt(parameter_to_be_fixed("prm_to_be_fixed"))
    + pp.Opt(parameter_name("prm_name"))
    + prm_opts_val("prm_value")
    + parameter_optional[...]
)("prm").add_parse_action(ast.PrmNode.parse_action)

#
# formula
#

func_name = pp.Word(pp.alphas, pp.alphanums + "_")("func_name")
func_empty_arg = pp.Empty().add_parse_action(lambda _: None)
func_args = pp.delimited_list(
    pp.Group(quoted_str | formula | func_empty_arg),
    allow_trailing_delim=True,
    delim=",",
).add_parse_action(ast.FunctionCallNode.func_args_parse_action)
func_call = (func_name + LPAR.suppress() + pp.Opt(func_args) + RPAR.suppress())(
    "func_call"
).add_parse_action(ast.FunctionCallNode.parse_action)

formula_element = (func_call | parameter)("formula_element")


def make_formula_unary_op(node: Type[ast.FormulaUnaryPlus]):
    "Create parsing element for unary compare operator"
    operator = pp.Literal(node.operator)("operator")
    operand = formula_element("operand")
    return pp.Group(operator + operand).add_parse_action(node.parse_action)


formula_unary_plus_op = make_formula_unary_op(ast.FormulaUnaryPlus)
formula_unary_minus_op = make_formula_unary_op(ast.FormulaUnaryMinus)


def make_formula_binary_op(node: Type[ast.FormulaAdd]):
    "Create parsing element for binary compare operator"
    operator = pp.Literal(node.operator)("operator")
    operand = formula_element("operand")
    return pp.Group(operand + operator + operand).add_parse_action(node.parse_action)


formula_add_op = make_formula_binary_op(ast.FormulaAdd)
formula_sub_op = make_formula_binary_op(ast.FormulaSub)
formula_mul_op = make_formula_binary_op(ast.FormulaMul)
formula_div_op = make_formula_binary_op(ast.FormulaDiv)
formula_exp_op = make_formula_binary_op(ast.FormulaExp)
formula_eq_op = make_formula_binary_op(ast.FormulaEQ)
formula_ne_op = make_formula_binary_op(ast.FormulaNE)
formula_le_op = make_formula_binary_op(ast.FormulaLE)
formula_lt_op = make_formula_binary_op(ast.FormulaLT)
formula_ge_op = make_formula_binary_op(ast.FormulaGE)
formula_gt_op = make_formula_binary_op(ast.FormulaGT)

formula_arith_expr = pp.helpers.infix_notation(
    formula_element,
    [
        (x.operator, x.num_operands, x.assoc, x.parse_action)
        for x in ast.FormulaNode.formula_arith_op_clses  # pylint: disable=not-an-iterable
    ],
    lpar=LPAR.suppress(),
    rpar=RPAR.suppress(),
)
formula_comp_expr = pp.helpers.infix_notation(
    formula_arith_expr,
    [
        (x.operator, x.num_operands, x.assoc, x.parse_action)
        for x in ast.FormulaNode.formula_comp_op_clses  # pylint: disable=not-an-iterable
    ],
)
formula <<= (formula_comp_expr)("formula")
formula.add_parse_action(ast.FormulaNode.parse_action)

# The local keyword is used for defining named parameters
# as local to the top, xdd or phase level
local = (
    (
        pp.Keyword("local").suppress()
        + parameter_name("prm_name")
        + (parameter_value | parameter_equation)("prm_value")
    )
    .set_results_name("local")
    .add_parse_action(ast.LocalNode.parse_action)
)


# [existing_prm E]...
# Allowed operators for existing_prm are +=, -=, *-, /= and ^=
EXISTING_PRM_OPERATOR = pp.one_of("+= -= *- /= ^= =")("existing_prm_operator")
existing_prm = (
    (
        pp.Keyword("existing_prm").suppress()
        + parameter_name
        + EXISTING_PRM_OPERATOR
        + formula("formula")
        + SEMICOLON.suppress()
    )
    .set_results_name("existing_prm")
    .add_parse_action(ast.ExistingPrmNode.parse_action)
)

# Typically, an INP file is run once; num_runs change’s this behavior
# where the refinement is restarted and performed again until it is
# performed num_runs times.
num_runs = (
    (pp.Keyword("num_runs").suppress() + (integer("nums") ^ parameter_name("nums")))
    .set_results_name("num_runs")
    .add_parse_action(ast.NumRunsNode.parse_action)
)


# [xdd $file [{ $data }] [range #] [xye_format] [gsas_format] [fullprof_format] ]...
# [gui_reload]
# [gui_ignore]
# Defines the start of xdd dependent keywords
# and the file containing the observed data.
xdd_filename = string_val("xdd_filename").add_parse_action(toks_pop_action)
xdd_inline_data = (
    pp.Literal("{").suppress()
    + pp.Opt(
        pp.Keyword("_xy")("xdd_data_xy").add_parse_action(lambda toks: toks[0] == "_xy")
    )
    + number[1, ...]("xdd_data")
    + pp.Literal("}").suppress()
).set_results_name("xdd_inline_data")
xdd_optional = (
    (pp.Keyword("range").suppress() + number("xdd_range"))
    | pp.Keyword("xye_format")("xye_format").add_parse_action(
        lambda toks: toks[0] == "xye_format"
    )
    | pp.Keyword("gsas_format")("gsas_format").add_parse_action(
        lambda toks: toks[0] == "gsas_format"
    )
    | pp.Keyword("fullprof_format")("fullprof_format").add_parse_action(
        lambda toks: toks[0] == "fullprof_format"
    )
    | pp.Keyword("gui_reload")("gui_reload").add_parse_action(
        lambda toks: toks[0] == "gui_reload"
    )
    | pp.Keyword("gui_ignore")("gui_ignore").add_parse_action(
        lambda toks: toks[0] == "gui_ignore"
    )
)
xdd = (
    pp.Keyword("xdd").suppress() + (xdd_inline_data | xdd_filename) + xdd_optional[...]
)("xdd").add_parse_action(ast.XddNode.parse_action)


# [axial_conv]...
#   filament_length E sample_length E receiving_slit_length E
#   [primary_soller_angle E]
#   [secondary_soller_angle E]
#   [axial_n_beta !E]
# Full axial divergence model using the method of Cheary & Coelho

axial_conv_filament_length = pp.Keyword("filament_length").suppress() + parameter(
    "filament_length"
)
axial_conv_sample_length = pp.Keyword("sample_length").suppress() + parameter(
    "sample_length"
)
axial_conv_receiving_slit_length = pp.Keyword(
    "receiving_slit_length"
).suppress() + parameter("receiving_slit_length")
axial_conv_primary_soller_angle = pp.Keyword(
    "primary_soller_angle"
).suppress() + parameter("primary_soller_angle")
axial_conv_secondary_soller_angle = pp.Keyword(
    "secondary_soller_angle"
).suppress() + parameter("secondary_soller_angle")
axial_conv_axial_n_beta = pp.Keyword("axial_n_beta").suppress() + parameter(
    "axial_n_beta"
)
axial_conv_optional = (
    axial_conv_primary_soller_angle
    | axial_conv_secondary_soller_angle
    | axial_conv_axial_n_beta
)
axial_conv = (
    pp.Keyword("axial_conv").suppress()
    + axial_conv_filament_length
    + axial_conv_sample_length
    + axial_conv_receiving_slit_length
    + axial_conv_optional[...]
)("axial_conv").add_parse_action(ast.AxialConvNode.parse_action)


# Macros are defined using the macro directive;
# Macros can have multiple arguments or none
macro_name = pp.Word(pp.alphas, pp.alphanums + "_")("macro_name")
macro_args = LPAR.suppress() + pp.Opt(func_args) + RPAR.suppress()
macro_statement = (
    prm
    | local
    | existing_prm
    | num_runs
    | xdd
    | axial_conv
    | formula
    | line_break
    | quoted_str
    | pp.OneOrMore(text, stop_on=pp.Literal("}")) # NOTE: no nested {}
)("macro_statement")
macro_statement.ignore(line_comment)
macro_statement.ignore(block_comment)
macro_body = (
    pp.Literal("{").suppress()
    + macro_statement[...]("macro_statements")
    + pp.Literal("}").suppress()
)
macro = (
    pp.Keyword("macro") + macro_name + pp.Opt(macro_args)("macro_args") + macro_body
)("macro").add_parse_action(ast.MacroNode.parse_action)


root = (
    prm
    | local
    | existing_prm
    | num_runs
    | xdd
    | axial_conv
    | macro
    | formula
    | line_break
    | text
)[...]
root.set_parse_action(ast.RootNode.parse_action)
root.ignore(line_comment)
root.ignore(block_comment)
