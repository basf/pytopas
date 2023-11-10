"Syntax tree"

from __future__ import annotations
from abc import ABC, abstractclassmethod, abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from functools import cache
from dataclasses import dataclass
from typing import Any, Dict, List, Self, Tuple, Type, TypeVar, Union, Optional, cast
from warnings import warn

import pyparsing as pp
from pyparsing.results import ParseResults

from .exc import ParseException, ParseWarning

from .trivial import number, LPAR, RPAR


BaseNodeT = TypeVar("BaseNodeT", bound="BaseNode")


@dataclass
class BaseNode(ABC):
    type = "base"
    # children: List[BaseNode] = field(default_factory=list, init=False)

    @abstractclassmethod
    def get_parser(cls) -> pp.ParserElement:
        "Return parser"
        ...

    @classmethod
    def parse(cls, text, permissive=True) -> Union[Self, FallbackNode]:
        "Try to parse text with optional fallback"
        try:
            return cast(BaseNode, cls.get_parser().parse_string(text).pop())
        except pp.ParseException as err:
            if permissive:
                warn(err.explain(), category=ParseWarning)
                return FallbackNode.parse(text)
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
        assert len(something) > 1
        type_name = something[0]
        for kind in kinds:
            if type_name == kind.type:
                return cast(BaseNodeT, kind.unserialize(something))
        raise TypeError(f"Unknown type {type_name}")


Trivial = Union[None, bool, int, float, str, Sequence["Trivial"], Dict[str, "Trivial"]]
NodeSerialized = list[Trivial]


@dataclass
class FallbackNode(BaseNode):
    "Last chance node"
    type = "fallback"
    value: str

    @classmethod
    @cache
    def get_parser(cls):
        return pp.Empty().add_parse_action(lambda text, loc, toks: cls(value=text))

    def unparse(self) -> str:
        return self.value

    def serialize(self) -> NodeSerialized:
        return [self.type, self.value]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) >= 2
        assert data[0] == cls.type
        assert isinstance(data[1], str)
        return cls(value=data[1])


@dataclass
class ParameterNameNode(BaseNode):
    "Parameter name"
    type = "parameter_name"
    name: str

    @classmethod
    @cache
    def get_parser(cls):
        # The first character can be an upper or lower-case letter.
        # Subsequent characters can include the underscore character '_'
        # and the numbers 0 through 9.
        parser = pp.Word(pp.alphas, pp.alphanums + "_").set_results_name("name")
        parser.add_parse_action(lambda toks: cls(name=cast(str, toks[0])))
        return parser

    def unparse(self) -> str:
        return self.name

    def serialize(self) -> NodeSerialized:
        return [self.type, self.unparse()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) >= 2
        assert data[0] == cls.type
        assert isinstance(data[1], str)
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
    def get_parser(cls):
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

        return parser.add_parse_action(action)

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
        assert len(data) >= 2
        assert data[0] == cls.type
        assert isinstance(data[1], str)
        return cls.parse(data[1])


@dataclass
class FormulaElementNode(BaseNode):
    "Formula base element TODO make me real"
    type = "formula_element"
    value: float

    @classmethod
    @cache
    def get_parser(cls):
        def action(toks):
            return cls(value=toks[0])

        return (
            number.copy().set_results_name("formula_element").add_parse_action(action)
        )

    def unparse(self):
        return str(self.value)

    def serialize(self) -> NodeSerialized:
        return [self.type, self.value]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) >= 2
        assert data[0] == cls.type
        assert isinstance(data[1], (int, float))
        return cls(value=data[1])


@dataclass
class FormulaUnaryPlus(BaseNode):
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
    def get_parser(cls):
        return pp.Group(
            pp.Literal(cls.operator).set_results_name("operator")
            + FormulaElementNode.get_parser().set_results_name("operand")
        ).add_parse_action(cls.from_tokens)

    def unparse(self):
        return " ".join([self.operator, self.operand.unparse()])

    def serialize(self) -> NodeSerialized:
        return [self.type, self.operand.serialize()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) == 2
        typ, operand_serial = data
        assert typ == cls.type
        kinds = (FormulaElementNode, *formula_arith_op_cls, FallbackNode)
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
class FormulaAdd(BaseNode):
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
    def get_parser(cls):
        operand = (
            FormulaElementNode.get_parser() | FallbackNode.get_parser()
        ).set_results_name("operand")

        operator = pp.Literal(cls.operator).set_results_name("operator")
        return pp.Group(operand + operator + operand).add_parse_action(cls.from_tokens)

    def unparse(self):
        "Unparse and add brackets"
        precendence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
        out = []
        for operand in self.operands:
            parentheses = False
            operand_src = operand.unparse()
            if isinstance(operand, formula_arith_op_cls):
                op = cast(FormulaArithOps, operand)
                if (
                    op.num_operands > 1
                    and op.assoc == pp.helpers.OpAssoc.LEFT
                    and (
                        precendence.get(self.operator, 1)
                        > precendence.get(op.operator, 1)
                    )
                ):
                    parentheses = True

            out.append(f"( {operand_src} )" if parentheses else operand_src)
        return f" {self.operator} ".join(out)

    def serialize(self) -> NodeSerialized:
        return [self.type, *[x.serialize() for x in self.operands]]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) > 2
        typ, *operands = data
        assert typ == cls.type
        kinds = (
            FormulaElementNode,
            *formula_arith_op_cls,
            *formula_comp_op_cls,
            FallbackNode,
        )
        return cls(operands=[cls.match_unserialize(kinds, x) for x in operands])


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
formula_arith_op_cls: Tuple[Type[FormulaArithOps], ...] = (
    FormulaUnaryPlus,
    FormulaUnaryMinus,
    FormulaExp,
    FormulaMul,
    FormulaDiv,
    FormulaSub,
    FormulaAdd,
)


@dataclass
class FormulaEQ(FormulaAdd):
    "Formula equality comparison operation"
    type = "=="
    operator = "=="

    # @classmethod
    # def from_tokens(cls, toks: ParseResults):
    #     """
    #     Create instance from _list_ of tokens
    #     Used by local parser and by infix notation's op list
    #     """
    #     operands = [x for x in toks[0] if x != cls.operator]
    #     return cls(operands=operands)

    # @classmethod
    # @cache
    # def get_parser(cls):
    #     operand = (
    #         FormulaElementNode.get_parser() | FallbackNode.get_parser()
    #     ).set_results_name("operand")

    #     operator = pp.Literal(cls.operator).set_results_name("operator")
    #     return pp.Group(operand + operator + operand).add_parse_action(cls.from_tokens)

    def unparse(self):
        "Unparse and add brackets"
        # precendence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
        # out = []
        # for operand in self.operands:
        #     parentheses = False
        #     operand_src = operand.unparse()
        #     if isinstance(operand, formula_arith_op_cls):
        #         op = cast(FormulaArithOps, operand)
        #         if (
        #             op.num_operands > 1
        #             and op.assoc == pp.helpers.OpAssoc.LEFT
        #             and (
        #                 precendence.get(self.operator, 1)
        #                 > precendence.get(op.operator, 1)
        #             )
        #         ):
        #             parentheses = True

        #     out.append(f"( {operand_src} )" if parentheses else operand_src)
        return f" {self.operator} ".join([x.unparse() for x in self.operands])

    # def serialize(self) -> NodeSerialized:
    #     return [self.type, *[x.serialize() for x in self.operands]]

    # @classmethod
    # def unserialize(cls, data: list[Any]):
    #     assert len(data) > 2
    #     typ, *operands = data
    #     assert typ == cls.type
    #     kinds = (FormulaElementNode, *formula_arith_op_cls, FallbackNode)
    #     return cls(operands=[cls.match_unserialize(kinds, x) for x in operands])


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
formula_comp_op_cls: Tuple[Type[FormulaCompOps], ...] = (
    FormulaEQ,
    FormulaNE,
    FormulaLE,
    FormulaLT,
    FormulaGE,
    FormulaGT,
)
FormulaValue = Union[FormulaElementNode, FormulaArithOps, FallbackNode]


@dataclass
class FormulaNode(BaseNode):
    "Infix notation formula node"
    type = "formula"
    value: FormulaValue

    @classmethod
    @cache
    def get_parser(cls):
        arith_expr = pp.helpers.infix_notation(
            FormulaElementNode.get_parser(),
            [
                (x.operator, x.num_operands, x.assoc, x.from_tokens)
                for x in formula_arith_op_cls
            ],
            lpar=LPAR.suppress(),
            rpar=RPAR.suppress(),
        )

        comp_expr = pp.helpers.infix_notation(
            arith_expr,
            [
                (x.operator, x.num_operands, x.assoc, x.from_tokens)
                for x in formula_comp_op_cls
            ],
        ).set_results_name("formula")
        comp_expr.add_parse_action(lambda toks: cls(value=cast(FormulaValue, toks[0])))
        return comp_expr

    def unparse(self) -> str:
        return self.value.unparse()

    def serialize(self) -> NodeSerialized:
        return [self.type, self.value.serialize()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) == 2
        typ, val = data
        assert typ == cls.type
        kinds = (
            FormulaElementNode,
            *formula_arith_op_cls,
            *formula_comp_op_cls,
            FallbackNode,
        )
        return cls(value=cls.match_unserialize(kinds, val))
