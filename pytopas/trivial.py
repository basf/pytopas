"Trivial grammar"
import pyparsing as pp
from pyparsing import (
    White,
    Word,
    Combine,
    Opt,
    Literal,
    OneOrMore,
    Regex,
)
from pyparsing.results import ParseResults

pp.ParserElement.enablePackrat()


EQUALS = Literal("=")
COLON = Literal(":")
SEMICOLON = Literal(";")
LPAR = Literal("(")
RPAR = Literal(")")

# comments
line_comment = Regex(r"'.*").suppress().set_results_name("line_comment")
block_comment = pp.c_style_comment.suppress().set_results_name("block_comment")


# simple numbers
integer = pp.common.integer("integer")
signed_integer = pp.common.signed_integer("signed_integer")
real = pp.common.real("real")
number = pp.common.number("number")


#
# strings
#


def quoted_str_action(toks: ParseResults):
    "Undoublequote string action"
    tok = toks[0]
    result = (
        tok.strip('"')
        if isinstance(tok, str) and tok.startswith('"') and tok.endswith('"')
        else tok
    )
    return result


simple_str = Word(pp.printables).set_results_name("simple_str")
ws_escaped_str = Combine(
    Word(pp.printables, exclude_chars="\\'")
    + OneOrMore(
        (Literal("\\").suppress() + White())
        + Opt(Word(pp.printables, exclude_chars="\\'"))
    ),
    adjacent=True,
).set_results_name("ws_escaped_str")
quoted_str = pp.dbl_quoted_string.set_results_name("quoted_str").add_parse_action(
    quoted_str_action
)
string_val = (
    (quoted_str | ws_escaped_str | simple_str)
    .set_results_name("string_val")
    .streamline()
)

#
# Parameters
#

parameter_to_be_fixed = (
    pp.Literal("!")
    .add_parse_action(lambda toks: toks[0] == "!")
    .set_results_name("to_be_fixed")
)
parameter_to_be_refined = (
    pp.Literal("@")
    .add_parse_action(lambda toks: toks[0] == "@")
    .set_results_name("to_be_refined")
)
