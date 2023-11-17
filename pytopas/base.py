"Syntax tree"

from __future__ import annotations
from abc import ABC, abstractclassmethod, abstractmethod
from collections.abc import Sequence
from functools import cache
from dataclasses import dataclass, field
from typing import Any, Dict, List, Self, Tuple, Type, TypeVar, Union, Optional, cast
from warnings import warn

import pyparsing as pp
from pyparsing.results import ParseResults

from .exc import ParseException, ParseWarning, ReconstructException

from .trivial import number, LPAR, RPAR


BaseNodeT = TypeVar("BaseNodeT", bound="BaseNode")


class DepsMixin:
    "Dependencies mixin"

    @classmethod
    @property
    def fallback_cls(cls):
        return FallbackNode

    @classmethod
    @property
    def line_break_cls(cls):
        return LineBreakNode

    @classmethod
    @property
    def formula_element_cls(cls):
        return FormulaElementNode

    @classmethod
    @property
    def formula_unary_plus_cls(cls):
        return FormulaUnaryPlus

    @classmethod
    @property
    def formula_unary_minus_cls(cls):
        return FormulaUnaryMinus

    @classmethod
    @property
    def formula_add_cls(cls):
        return FormulaAdd

    @classmethod
    @property
    def formula_sub_cls(cls):
        return FormulaSub

    @classmethod
    @property
    def formula_mul_cls(cls):
        return FormulaMul

    @classmethod
    @property
    def formula_div_cls(cls):
        return FormulaDiv

    @classmethod
    @property
    def formula_exp_cls(cls):
        return FormulaExp

    @classmethod
    @property
    def formula_arith_op_clses(cls) -> tuple[Type[FormulaArithOps], ...]:
        return (
            cls.formula_unary_plus_cls,
            cls.formula_unary_minus_cls,
            cls.formula_exp_cls,
            cls.formula_mul_cls,
            cls.formula_div_cls,
            cls.formula_sub_cls,
            cls.formula_add_cls,
        )

    @classmethod
    @property
    def formula_eq_cls(cls):
        return FormulaEQ

    @classmethod
    @property
    def formula_ne_cls(cls):
        return FormulaNE

    @classmethod
    @property
    def formula_le_cls(cls):
        return FormulaLE

    @classmethod
    @property
    def formula_lt_cls(cls):
        return FormulaLT

    @classmethod
    @property
    def formula_ge_cls(cls):
        return FormulaGE

    @classmethod
    @property
    def formula_gt_cls(cls):
        return FormulaGT

    @classmethod
    @property
    def formula_comp_op_clses(cls) -> Tuple[Type[FormulaCompOps], ...]:
        return (
            cls.formula_eq_cls,
            cls.formula_ne_cls,
            cls.formula_le_cls,
            cls.formula_lt_cls,
            cls.formula_ge_cls,
            cls.formula_gt_cls,
        )

    @classmethod
    @property
    def formula_cls(cls):
        return FormulaNode


@dataclass
class BaseNode(ABC, DepsMixin):
    type = "base"

    @classmethod
    def _wrap_fallback(cls, parser: pp.ParserElement):
        "Wrap parser with match first and fallback"
        fallback_parser = cls.fallback_cls.get_parser()
        return pp.MatchFirst([parser, fallback_parser])

    @abstractclassmethod
    def get_parser(cls, permissive=True) -> pp.ParserElement:
        "Return parser"
        ...

    @classmethod
    def parse(cls, text, permissive=True, parse_all=False) -> Union[Self, FallbackNode]:
        "Try to parse text with optional fallback"
        try:
            result = cls.get_parser(permissive).parse_string(text, parse_all=parse_all)
            return cast(BaseNode, result.pop())
        except pp.ParseException as err:
            if permissive:
                warn(err.explain(), category=ParseWarning)
                return cls.fallback_cls.parse(text, permissive=False)
            raise ParseException(err.pstr, err.loc, err.msg) from err

    @abstractmethod
    def unparse(self) -> str:
        "Reconstruct source code from Node"
        ...

    @abstractmethod
    def serialize(self) -> NodeSerialized:
        "Node representation as json-compatible tuples"
        ...

    @abstractclassmethod
    def unserialize(cls, data: list[Any]) -> Self:
        "Reconstruct node from dictionary"
        ...

    @staticmethod
    def match_unserialize(
        kinds: Tuple[Type[BaseNodeT], ...], something: Any
    ) -> BaseNodeT:
        "Helper method for unserializing of tuples"
        if not hasattr(something, "__len__") or len(something) < 1:
            raise ReconstructException("assert len > 1", something)
        type_name = something[0]
        for kind in kinds:
            if type_name == kind.type:
                return cast(BaseNodeT, kind.unserialize(something))
        raise ReconstructException(
            f"assert data[0] in [{','.join(x.type for x in kinds)}]", something
        )


Trivial = Union[None, bool, int, float, str, Sequence["Trivial"], Dict[str, "Trivial"]]
NodeSerialized = list[Trivial]


@dataclass
class FallbackNode(BaseNode):
    "Last chance node"
    type = "fallback"
    value: str

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        def make_warn_action(text: str, loc: int, _):
            new_text = text[loc : 100 + loc]
            msg = f"FallbackNode: Can't parse text '{new_text}'"
            return warn(msg, category=ParseWarning)

        parser = pp.Regex(r"\S+").set_results_name("unknown")
        parser.add_parse_action(
            lambda toks: cls(value=cast(str, toks.unknown))
        )
        return parser.add_parse_action(make_warn_action)

    def unparse(self) -> str:
        return self.value

    def serialize(self) -> NodeSerialized:
        return [self.type, self.value]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        if not isinstance(data[1], str):
            raise ReconstructException("assert type(data[1]) == str", data)
        return cls(value=data[1])


@dataclass
class LineBreakNode(BaseNode):
    "Line break"
    type = "lb"

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        parser = pp.LineEnd().set_results_name("line_break")
        parser.add_parse_action(lambda _: cls())
        return parser

    def unparse(self) -> str:
        return "\n"

    def serialize(self) -> NodeSerialized:
        return [self.type]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 1:
            raise ReconstructException("assert len >= 1", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        return cls()


@dataclass
class ParameterNameNode(BaseNode):
    "Parameter name"
    type = "parameter_name"
    name: str

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        # The first character can be an upper or lower-case letter.
        # Subsequent characters can include the underscore character '_'
        # and the numbers 0 through 9.
        parser = pp.Word(pp.alphas, pp.alphanums + "_").set_results_name("name")
        parser.add_parse_action(lambda toks: cls(name=cast(str, toks.name)))
        return cls._wrap_fallback(parser) if permissive else parser

    def unparse(self) -> str:
        return self.name

    def serialize(self) -> NodeSerialized:
        return [self.type, self.unparse()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        if not isinstance(data[1], str):
            raise ReconstructException("assert type(data[1]) == str", data)
        return cls(name=data[1])


@dataclass
class ParameterValueNode(BaseNode):
    "Parameter node"
    type = "parameter_value"
    # The character ! placed before name signals that parameter is not to be refined
    # TODO: to_be_fixed: bool = False
    # A parameter can also be flagged for refinement by placing
    # the @ character at the start of its name
    # TODO: to_be_refined: bool = False
    value: float
    esd: Optional[float] = None
    backtick: bool = False
    lim_min: Optional[float] = None
    lim_max: Optional[float] = None

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        backtick_parser = (
            pp.Literal("`")
            .add_parse_action(lambda toks: toks[0] == "`")
            .set_results_name("backtick")
        )
        lim_min_parser = pp.Literal("_LIMIT_MIN_") + number.set_results_name("lim_min")
        lim_max_parser = pp.Literal("_LIMIT_MAX_") + number.set_results_name("lim_max")
        parser = pp.Combine(
            number("value")
            + pp.Opt(backtick_parser)
            + pp.Opt("_" + number("esd"))
            + pp.Opt(pp.Opt(lim_min_parser) & pp.Opt(lim_max_parser)),
            adjacent=True,
            join_string="",
        ).set_results_name("parameter_value")

        def action(toks):
            tok = cast(ParseResults, toks[0]).as_dict()
            node = cls(value=tok["value"])
            node.esd = tok.get("esd", None)
            node.backtick = tok.get("backtick", False)
            node.lim_min = tok.get("lim_min", False)
            node.lim_max = tok.get("lim_max", False)
            return node

        parser.add_parse_action(action)
        return cls._wrap_fallback(parser) if permissive else parser

    def unparse(self) -> str:
        backtick_part = self.backtick and "`" or ""
        esd_part = self.esd is not None and f"_{self.esd}" or ""
        lim_min_part = self.lim_min is not None and f"_LIMIT_MIN_{self.lim_min}" or ""
        lim_max_part = self.lim_max is not None and f"_LIMIT_MAX_{self.lim_max}" or ""
        return f"{self.value}{backtick_part}{esd_part}{lim_min_part}{lim_max_part}"

    def serialize(self) -> NodeSerialized:
        return [self.type, self.unparse()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        if not isinstance(data[1], str):
            raise ReconstructException("assert type(data[1]) == str", data)
        return cls.parse(data[1])


@dataclass
class FormulaElementNode(BaseNode):
    "Formula base element TODO make me real"
    type = "formula_element"
    value: float

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        parser = (
            number.copy()
            .set_results_name("formula_element")
            .add_parse_action(lambda toks: cls(value=cast(float, toks.formula_element)))
        )
        return cls._wrap_fallback(parser) if permissive else parser

    def unparse(self):
        return str(self.value)

    def serialize(self) -> NodeSerialized:
        return [self.type, self.value]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        # TODO: assert
        assert isinstance(data[1], (int, float))
        return cls(value=data[1])


@dataclass
class FormulaOp(BaseNode):
    "Formula base operator"
    operator: str = field(init=False)
    assoc: pp.helpers.OpAssoc = field(init=False)
    num_operands: int = field(init=False)


@dataclass
class FormulaUnaryPlus(FormulaOp):
    "Formula unary plus operation"
    type = "+1"
    operator = "+"
    operand: FormulaValue
    num_operands = 1
    assoc = pp.helpers.OpAssoc.RIGHT

    @classmethod
    def from_tokens(cls, toks: ParseResults):
        """
        Create instance from _list_ of tokens
        Used by local parser and by infix notation's op list
        """
        _, operand = toks[0]
        return operand

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        formula_el = cls.formula_element_cls.get_parser(permissive)
        parser = pp.Group(
            pp.Literal(cls.operator).set_results_name("operator")
            + formula_el.set_results_name("operand")
        )
        parser.add_parse_action(cls.from_tokens)
        return cls._wrap_fallback(parser) if permissive else parser

    def unparse(self):
        return " ".join([self.operator, self.operand.unparse()])

    def serialize(self) -> NodeSerialized:
        return [self.type, self.operand.serialize()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) != 2:
            raise ReconstructException("assert len == 2", data)
        typ, operand_serial = data
        if typ != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        kinds = (
            cls.formula_element_cls,
            *cls.formula_arith_op_clses,
            cls.fallback_cls,
        )
        operand = cls.match_unserialize(kinds, operand_serial)
        return cls(operand=operand)


@dataclass
class FormulaUnaryMinus(FormulaUnaryPlus):
    "Formula unary plus operation"
    type = "-1"
    operator = "-"

    @classmethod
    def from_tokens(cls, toks: ParseResults):
        """
        Create instance from _list_ of tokens
        Used by local parser and by infix notation's op list
        """
        _, operand = toks[0]
        if isinstance(operand, FormulaElementNode) and isinstance(
            operand.value, (int, float)
        ):
            return FormulaElementNode(value=-operand.value)
        return cls(operand=cast(FormulaElementNode, operand))


@dataclass
class FormulaAdd(FormulaOp):
    "Formula addition operation"
    type = "+"
    operator = "+"
    operands: List[FormulaValue]
    num_operands = 2
    assoc = pp.helpers.OpAssoc.LEFT

    @classmethod
    def from_tokens(cls, toks: ParseResults):
        """
        Create instance from _list_ of tokens
        Used by local parser and by infix notation's op list
        """
        operands = [x for x in toks[0] if x != cls.operator]
        return cls(operands=operands)

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        formula_el = cls.formula_element_cls.get_parser(permissive)
        fallback = cls.fallback_cls.get_parser(permissive)
        operand = pp.MatchFirst([formula_el, fallback]).set_results_name("operand")

        operator = pp.Literal(cls.operator).set_results_name("operator")
        parser = pp.Group(operand + operator + operand)
        parser.add_parse_action(cls.from_tokens)
        return cls._wrap_fallback(parser) if permissive else parser

    def unparse(self):
        "Unparse and add brackets"
        precendence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
        out = []
        for operand in self.operands:
            parentheses = False
            operand_src = operand.unparse()
            if isinstance(operand, self.formula_arith_op_clses):
                if (
                    operand.num_operands > 1
                    and operand.assoc == pp.helpers.OpAssoc.LEFT
                    and (
                        precendence.get(self.operator, 1)
                        > precendence.get(operand.operator, 1)
                    )
                ):
                    parentheses = True

            out.append(f"( {operand_src} )" if parentheses else operand_src)
        return f" {self.operator} ".join(out)

    def serialize(self) -> NodeSerialized:
        return [self.type, *[x.serialize() for x in self.operands]]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) <= 2:
            raise ReconstructException("assert len > 2", data)
        typ, *operands = data
        if typ != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        kinds = (
            cls.formula_element_cls,
            *cls.formula_arith_op_clses,
            *cls.formula_comp_op_clses,
            cls.fallback_cls,
        )
        ops = [cls.match_unserialize(kinds, x) for x in operands]
        return cls(operands=ops)


@dataclass
class FormulaSub(FormulaAdd):
    "Formula subtraction operation"
    type = "-"
    operator = "-"


@dataclass
class FormulaMul(FormulaAdd):
    "Formula multiplication operation"
    type = "*"
    operator = "*"


@dataclass
class FormulaDiv(FormulaAdd):
    "Formula division operation"
    type = "/"
    operator = "/"


@dataclass
class FormulaExp(FormulaAdd):
    "Formula expanentiation operation"
    type = "^"
    operator = "^"


FormulaArithOps = Union[
    FormulaUnaryPlus,
    FormulaUnaryMinus,
    FormulaExp,
    FormulaMul,
    FormulaDiv,
    FormulaSub,
    FormulaAdd,
]


@dataclass
class FormulaEQ(FormulaAdd):
    "Formula equality comparison operation"
    type = "=="
    operator = "=="

    def unparse(self):
        "Unparse and add brackets"
        return f" {self.operator} ".join([x.unparse() for x in self.operands])


@dataclass
class FormulaNE(FormulaAdd):
    "Formula not equality comparison operation"
    type = "!="
    operator = "!="


@dataclass
class FormulaLE(FormulaAdd):
    "Formula less comparison operation"
    type = "<"
    operator = "<"


@dataclass
class FormulaLT(FormulaAdd):
    "Formula less than comparison operation"
    type = "<="
    operator = "<="


@dataclass
class FormulaGE(FormulaAdd):
    "Formula greater comparison operation"
    type = ">"
    operator = ">"


@dataclass
class FormulaGT(FormulaAdd):
    "Formula greater than comparison operation"
    type = ">="
    operator = ">="


FormulaCompOps = Union[
    FormulaEQ,
    FormulaNE,
    FormulaLE,
    FormulaLT,
    FormulaGE,
    FormulaGT,
]
FormulaValue = Union[FormulaElementNode, FormulaArithOps, FormulaCompOps, FallbackNode]


@dataclass
class FormulaNode(BaseNode):
    "Infix notation formula node"
    type = "formula"
    value: FormulaValue

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        formula_el = cls.formula_element_cls.get_parser(permissive)
        arith_expr = pp.helpers.infix_notation(
            formula_el,
            [
                (x.operator, x.num_operands, x.assoc, x.from_tokens)
                for x in cls.formula_arith_op_clses
            ],
            lpar=LPAR.suppress(),
            rpar=RPAR.suppress(),
        )

        parser = pp.helpers.infix_notation(
            arith_expr,
            [
                (x.operator, x.num_operands, x.assoc, x.from_tokens)
                for x in cls.formula_comp_op_clses
            ],
        ).set_results_name("formula")
        parser.add_parse_action(
            lambda toks: cls(value=cast(FormulaValue, toks.formula))
        )
        return cls._wrap_fallback(parser) if permissive else parser

    def unparse(self) -> str:
        return self.value.unparse()

    def serialize(self) -> NodeSerialized:
        return [self.type, self.value.serialize()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) != 2:
            raise ReconstructException("assert len == 2", data)
        typ, val = data
        if typ != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        kinds = (
            cls.formula_element_cls,
            *cls.formula_arith_op_clses,
            *cls.formula_comp_op_clses,
            cls.fallback_cls,
        )
        return cls(value=cls.match_unserialize(kinds, val))
