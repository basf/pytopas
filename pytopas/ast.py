"Syntax tree"
# pylint: disable=too-many-lines

from __future__ import annotations

import json
import sys
import warnings
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from functools import reduce
from typing import Any, Dict, TypeVar, Union, cast

import pyparsing as pp
from pyparsing.results import ParseResults

from .exc import ParseWarning, ReconstructException

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


BaseNodeT = TypeVar("BaseNodeT", bound="BaseNode")


class DepsMixin:
    "Dependencies mixin"
    # pylint: disable=too-many-public-methods

    @staticmethod
    def get_grammar():
        "Get grammar module (workaround partially initialized module)"
        from . import grammar  # pylint: disable=import-outside-toplevel

        return grammar

    @classmethod
    @property
    def text_cls(cls):
        "Text node class"
        return TextNode

    @classmethod
    @property
    def line_break_cls(cls):
        "Line break node class"
        return LineBreakNode

    @classmethod
    @property
    def parameter_name_cls(cls):
        "Parameter name node class"
        return ParameterNameNode

    @classmethod
    @property
    def parameter_value_cls(cls):
        "Parameter value node class"
        return ParameterValueNode

    @classmethod
    @property
    def parameter_equation_cls(cls):
        "Parameter equation node class"
        return ParameterEquationNode

    @classmethod
    @property
    def parameter_cls(cls):
        "Parameter node class"
        return ParameterNode

    @classmethod
    @property
    def prm_cls(cls):
        "`prm` node class"
        return PrmNode

    @classmethod
    @property
    def func_call_cls(cls):
        "Formula function call class"
        return FunctionCallNode

    @classmethod
    @property
    def formula_unary_plus_cls(cls):
        "Formula unary + op class"
        return FormulaUnaryPlus

    @classmethod
    @property
    def formula_unary_minus_cls(cls):
        "Formula unary - op class"
        return FormulaUnaryMinus

    @classmethod
    @property
    def formula_add_cls(cls):
        "Formula + op class"
        return FormulaAdd

    @classmethod
    @property
    def formula_sub_cls(cls):
        "Formula - op class"
        return FormulaSub

    @classmethod
    @property
    def formula_mul_cls(cls):
        "Formula * op class"
        return FormulaMul

    @classmethod
    @property
    def formula_div_cls(cls):
        "Formula / op class"
        return FormulaDiv

    @classmethod
    @property
    def formula_exp_cls(cls):
        "Formula ^ op class"
        return FormulaExp

    @classmethod
    @property
    def formula_arith_op_clses(cls) -> tuple[type[FormulaArithOps], ...]:
        "Formula element unary operation classes"
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
        "Formula == op class"
        return FormulaEQ

    @classmethod
    @property
    def formula_ne_cls(cls):
        "Formula != op class"
        return FormulaNE

    @classmethod
    @property
    def formula_le_cls(cls):
        "Formula <= op class"
        return FormulaLE

    @classmethod
    @property
    def formula_lt_cls(cls):
        "Formula < op class"
        return FormulaLT

    @classmethod
    @property
    def formula_ge_cls(cls):
        "Formula >= op class"
        return FormulaGE

    @classmethod
    @property
    def formula_gt_cls(cls):
        "Formula > op class"
        return FormulaGT

    @classmethod
    @property
    def formula_comp_op_clses(cls) -> tuple[type[FormulaCompOps], ...]:
        "Formula element compare operation classes"
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
        "Formula class"
        return FormulaNode

    @classmethod
    @property
    def local_cls(cls):
        "Local class"
        return LocalNode


@dataclass
class BaseNode(ABC, DepsMixin):
    "Base node class"
    type = "base"

    @classmethod
    @abstractmethod
    def get_parser(cls) -> pp.ParserElement:  # noqa: B902
        "Return parser"

    @classmethod
    def parse(cls, text, parse_all=False, print_dump=False) -> Self | TextNode | None:
        "Try to parse text with optional fallback"
        try:
            result = cls.get_parser().parse_string(text, parse_all=parse_all)
            if print_dump:
                print(result.dump())
            return result.pop() if len(result) else None  # type: ignore[assigment]
        except pp.ParseException as err:
            warnings.warn(err.explain(), category=ParseWarning, stacklevel=3)
            return cls.text_cls.parse(text)

    @abstractmethod
    def unparse(self) -> str:
        "Reconstruct source code from Node"

    @abstractmethod
    def serialize(self) -> NodeSerialized:
        "Node representation as json-compatible tuples"

    @classmethod
    @abstractmethod
    def unserialize(cls, _: list[Any]) -> Self:  # noqa: B902
        "Reconstruct node from dictionary"

    @staticmethod
    def match_unserialize(
        kinds: tuple[type[BaseNodeT], ...], something: Any
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
class TextNode(BaseNode):
    "Last chance node"
    type = "text"
    value: str

    @classmethod
    def parse_action(cls, text: str, loc: int, toks: pp.ParseResults):
        "Parse action for the text parse element"
        short_text = text[loc : 100 + loc]
        warn_msg = f"TextNode: Can't parse text {short_text!r}"
        warnings.warn(warn_msg, category=ParseWarning, stacklevel=3)
        return cls(value=toks.as_list()[0])

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().text

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
    def parse_action(cls, _):
        "Parse action for the line break parse element"
        return cls()

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().line_break

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
    def parse_action(cls, toks: pp.ParseResults):
        "Parse action for the parameter name parse element"
        return cls(name=toks.as_list()[0])

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().parameter_name

    def unparse(self) -> str:
        return self.name

    def serialize(self) -> NodeSerialized:
        return [self.type, self.name]

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
    value: Decimal
    esd: Decimal | None = None
    backtick: bool = False
    lim_min: Decimal | None = None
    lim_max: Decimal | None = None

    @classmethod
    def parse_action(cls, toks: pp.ParseResults):
        "Parse action for the parameter parse element"
        data = toks[0]
        return cls(
            value=data.value,  # type: ignore[assignment]
            esd=data.get("esd", None),  # type: ignore[assignment]
            backtick=data.get("backtick", False),  # type: ignore[assignment]
            lim_min=data.get("lim_min", [None])[0],  # type: ignore[assignment]
            lim_max=data.get("lim_max", [None])[0],  # type: ignore[assignment]
        )

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().parameter_value

    def unparse(self) -> str:
        backtick_part = "`" if self.backtick else ""
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


ParameterEquationValue = Union["FormulaNode", TextNode]


@dataclass
class ParameterEquationNode(BaseNode):
    "Parameter equation like = a + 1; : 0"
    type = "prm_eq"
    formula: ParameterEquationValue
    reporting: ParameterValueNode | TextNode | None = None

    @classmethod
    @property
    def parameter_equation_value_clses(cls):
        "Parameter equation classes"
        return (cls.formula_cls, cls.text_cls)

    @classmethod
    @property
    def parameter_equation_reporting_clses(cls):
        "Parameter equation reporting classes"
        return (cls.parameter_value_cls, cls.text_cls)

    @classmethod
    def parse_action(cls, toks: pp.ParseResults):
        "Parse action for the parameter equation parse element"
        return cls(
            formula=toks.formula,  # type: ignore[assignment]
            reporting=toks.get("reporting", None),  # type: ignore[assignment]
        )

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().parameter_equation

    def unparse(self):
        equation = f"= {self.formula.unparse()};"
        return (
            equation
            if self.reporting is None
            else f"{equation} : {str(self.reporting.unparse())}"
        )

    def serialize(self) -> NodeSerialized:
        reporting = [self.reporting.serialize()] if self.reporting is not None else []
        return [self.type, self.formula.serialize(), *reporting]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        formula = cls.match_unserialize(cls.parameter_equation_value_clses, data[1])
        reporting = (
            None
            if len(data) < 3
            else cls.match_unserialize(cls.parameter_equation_reporting_clses, data[2])
        )
        return cls(formula, reporting)


ParameterValue = Union[ParameterValueNode, ParameterEquationNode, TextNode]


@dataclass
class ParameterNode(BaseNode):
    """
    [!|@] [name] [E]
      [min !E] [max !E] [del !E] [update !E]
      [stop_when !E] [val_on_continue !E]
    """

    # pylint: disable=too-many-instance-attributes

    type = "p"
    optional_keys = (
        "to_be_fixed",
        "to_be_refined",
        "name",
        "value",
        "min",
        "max",
        "del",
        "update",
        "stop_when",
        "val_on_continue",
    )
    short_keys = ("!", "@", "n", "v", "_", "^", "d", "u", "s", "c")
    prm_to_be_fixed: bool = False
    prm_to_be_refined: bool = False
    prm_name: ParameterNameNode | None = None
    prm_value: ParameterValue | None = None
    prm_min: ParameterValue | None = None
    prm_max: ParameterValue | None = None
    prm_del: ParameterValue | None = None
    prm_update: ParameterValue | None = None
    prm_stop_when: ParameterValue | None = None
    prm_val_on_continue: ParameterValue | None = None
    next: ParameterNode | None = None

    @classmethod
    @property
    def parameter_value_clses(cls):
        "Parameter's value classes"
        return (cls.parameter_value_cls, cls.parameter_equation_cls, cls.text_cls)

    @classmethod
    def parse_action(cls, toks: pp.ParseResults) -> Self:
        "Parse action for the parameter parse element"
        # case: multiple parameters without delimeter
        if isinstance(toks.as_list()[0], list) and len(toks.as_list()[0]) > 0:

            def mk_linked_params(
                prev: Self | None, data: ParameterNameNode | ParameterValueNode
            ):
                if isinstance(data, ParameterNameNode):
                    return cls(prm_name=data, next=prev)
                if isinstance(data, ParameterValueNode):
                    return cls(prm_value=data, next=prev)
                return None

            return cast(
                Self, reduce(mk_linked_params, reversed(toks.as_list()[0]), None)
            )

        # case: normal object
        param = cls()
        for key in map(lambda x: f"prm_{x}", cls.optional_keys):
            val = toks.get(key)
            if val is not None:
                setattr(param, key, val)
        return param

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().parameter

    def unparse(self):
        strings = []
        if self.prm_to_be_fixed:
            strings.append("!")
        if self.prm_to_be_refined:
            strings.append("@")
        for key in self.optional_keys:
            o_key = f"prm_{key}"
            val = getattr(self, o_key, None)
            if isinstance(val, BaseNode):
                if key in ["name", "value"]:
                    strings.append(val.unparse())
                else:
                    strings += [key, val.unparse()]
        if self.next:
            strings.append(self.next.unparse())
        return " ".join(strings)

    def serialize(self) -> NodeSerialized:
        short = {}
        if self.prm_to_be_fixed:
            short["!"] = True
        if self.prm_to_be_refined:
            short["@"] = True
        if self.next:
            short[">"] = self.next.serialize()

        prm_opt_keys = map(lambda x: f"prm_{x}", self.optional_keys)
        for d_key, s_key in zip(prm_opt_keys, self.short_keys):  # noqa: B905
            val = getattr(self, d_key, None)
            if isinstance(val, BaseNode):
                short[s_key] = val.serialize()
        return [self.type, short]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        opts = {}
        if len(data) and isinstance(data[1], dict):
            opts = data[1]
        else:
            raise ReconstructException("assert data[1] is dict", data)

        param = cls()
        prm_opt_keys = map(lambda x: f"prm_{x}", cls.optional_keys)
        for o_key, s_key in zip(prm_opt_keys, cls.short_keys):  # noqa: B905
            if s_key in opts and isinstance(opts[s_key], list):
                val = opts[s_key]
                if o_key == "prm_name":
                    param.prm_name = cls.parameter_name_cls.unserialize(val)
                elif o_key == "prm_value":
                    param.prm_value = cls.match_unserialize(
                        cls.parameter_value_clses, val
                    )
                else:
                    setattr(
                        param,
                        o_key,
                        cls.match_unserialize(cls.parameter_value_clses, val),
                    )
        if opts.get("!") is True:
            param.prm_to_be_fixed = True
        if opts.get("@") is True:
            param.prm_to_be_refined = True
        if opts.get(">") is not None:
            param.next = cls.unserialize(opts[">"])

        return param


@dataclass
class PrmNode(ParameterNode):
    "prm E [min !E] [max !E] [del !E] [update !E] [stop_when !E] [val_on_continue !E]"
    # pylint: disable=too-many-instance-attributes
    type = "prm"
    prm_value: ParameterValue
    prm_to_be_fixed: bool = False
    prm_to_be_refined: bool = field(default_factory=lambda: False, init=False)
    prm_name: ParameterNameNode | None = None
    prm_min: ParameterValue | None = None
    prm_max: ParameterValue | None = None
    prm_del: ParameterValue | None = None
    prm_update: ParameterValue | None = None
    prm_stop_when: ParameterValue | None = None
    prm_val_on_continue: ParameterValue | None = None
    next: None = field(default_factory=lambda: None, init=False)

    @classmethod
    def from_parameter(cls, param: ParameterNode):
        "Create from the parameter node"
        return cls(
            prm_to_be_fixed=param.prm_to_be_fixed,
            prm_value=param.prm_value,  # type: ignore[assigment]
            prm_name=param.prm_name,
            prm_min=param.prm_min,
            prm_max=param.prm_max,
            prm_del=param.prm_del,
            prm_update=param.prm_update,
            prm_stop_when=param.prm_stop_when,
            prm_val_on_continue=param.prm_val_on_continue,
        )

    @classmethod
    def parse_action(cls, toks: pp.ParseResults):
        param = cls.parameter_cls.parse_action(toks)
        return cls.from_parameter(param)

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().prm

    def unparse(self):
        return f"prm {super().unparse()}"

    def serialize(self) -> NodeSerialized:
        return [self.type, *super().serialize()[1:]]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        p_type = cls.parameter_cls.type
        param = cls.parameter_cls.unserialize([p_type, data[1]])
        return cls.from_parameter(param)


@dataclass
class FunctionCallNode(BaseNode):
    "Function call node like `sin(a)`"
    type = "func_call"
    name: str
    args: list[FormulaNode | str | None | TextNode] = field(default_factory=list)

    @classmethod
    def func_args_parse_action(cls, toks: pp.ParseResults):
        "Parse action for the args of the function call parse element"
        if len(toks.as_list()) == 1 and toks.as_list()[0] == []:
            return []
        return [(x[0] if len(x) else None) for x in toks.as_list()]

    @classmethod
    def parse_action(cls, toks: pp.ParseResults):
        "Parse action for the function call parse element"
        name, *args = toks.as_list()
        return cls(name=name, args=args)

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().func_call

    def unparse(self):
        args = []
        for x in self.args:
            if isinstance(x, BaseNode):
                args.append(x.unparse())
            if isinstance(x, str):
                args.append(json.dumps(x))
            if x is None:
                args.append("")
        return f"{self.name}({', '.join(args)})"

    def serialize(self) -> NodeSerialized:
        args = [(x.serialize() if isinstance(x, BaseNode) else x) for x in self.args]
        return [self.type, self.name, *args]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 2:
            raise ReconstructException("assert len >= 2", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        kinds = (
            cls.formula_cls,
            cls.text_cls,
        )
        args = [
            (
                cls.match_unserialize(kinds, x)
                if isinstance(x, list)
                else cast(Union[str, None], x)
            )
            for x in data[2:]
        ]
        return cls(name=data[1], args=args)


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
    def parse_action(cls, toks: ParseResults):
        """
        Create instance from _list_ of tokens
        Used by local parser and by infix notation's op list
        """
        _, operand = toks[0]
        return operand

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_unary_plus_op

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
            cls.func_call_cls,
            cls.parameter_cls,
            *cls.formula_arith_op_clses,
            cls.text_cls,
        )
        operand = cls.match_unserialize(kinds, operand_serial)
        return cls(operand=operand)


@dataclass
class FormulaUnaryMinus(FormulaUnaryPlus):
    "Formula unary plus operation"
    type = "-1"
    operator = "-"

    @classmethod
    def parse_action(cls, toks: ParseResults):
        """
        Create instance from _list_ of tokens
        Used by local parser and by infix notation's op list
        """
        _, operand = toks[0]
        return cls(operand=operand)

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_unary_minus_op


@dataclass
class FormulaAdd(FormulaOp):
    "Formula addition operation"
    type = "+"
    operator = "+"
    operands: list[FormulaValue]
    num_operands = 2
    assoc = pp.helpers.OpAssoc.LEFT

    @classmethod
    def parse_action(cls, toks: ParseResults):
        """
        Create instance from _list_ of tokens
        Used by local parser and by infix notation's op list
        """
        operands = [x for x in toks[0] if x != cls.operator]
        return cls(operands=operands)

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_add_op

    def unparse(self):
        "Unparse and add brackets"
        precendence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
        out = []
        for operand in self.operands:
            parentheses = False
            operand_src = operand.unparse()
            # pylint: disable=isinstance-second-argument-not-valid-type
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
            cls.func_call_cls,
            cls.parameter_cls,
            *cls.formula_arith_op_clses,
            *cls.formula_comp_op_clses,
            cls.text_cls,
        )
        ops = [cls.match_unserialize(kinds, x) for x in operands]
        return cls(operands=ops)


@dataclass
class FormulaSub(FormulaAdd):
    "Formula subtraction operation"
    type = "-"
    operator = "-"

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_sub_op


@dataclass
class FormulaMul(FormulaAdd):
    "Formula multiplication operation"
    type = "*"
    operator = "*"

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_mul_op


@dataclass
class FormulaDiv(FormulaAdd):
    "Formula division operation"
    type = "/"
    operator = "/"

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_div_op


@dataclass
class FormulaExp(FormulaAdd):
    "Formula expanentiation operation"
    type = "^"
    operator = "^"

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_exp_op


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

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_eq_op

    def unparse(self):
        "Unparse and add brackets"
        return f" {self.operator} ".join([x.unparse() for x in self.operands])


@dataclass
class FormulaNE(FormulaAdd):
    "Formula not equality comparison operation"
    type = "!="
    operator = "!="

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_ne_op


@dataclass
class FormulaLE(FormulaAdd):
    "Formula less comparison operation"
    type = "<"
    operator = "<"

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_le_op


@dataclass
class FormulaLT(FormulaAdd):
    "Formula less than comparison operation"
    type = "<="
    operator = "<="

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_lt_op


@dataclass
class FormulaGE(FormulaAdd):
    "Formula greater comparison operation"
    type = ">"
    operator = ">"

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_ge_op


@dataclass
class FormulaGT(FormulaAdd):
    "Formula greater than comparison operation"
    type = ">="
    operator = ">="

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula_gt_op


FormulaCompOps = Union[
    FormulaEQ,
    FormulaNE,
    FormulaLE,
    FormulaLT,
    FormulaGE,
    FormulaGT,
]
FormulaValue = Union[
    FunctionCallNode, ParameterNode, FormulaArithOps, FormulaCompOps, TextNode
]


@dataclass
class FormulaNode(BaseNode):
    "Infix notation formula node"
    type = "formula"
    value: FormulaValue

    @classmethod
    def parse_action(cls, toks: pp.ParseResults):
        "Parse action for the formula node"
        return cls(value=toks.as_list()[0])

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().formula

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
            cls.func_call_cls,
            cls.parameter_cls,
            *cls.formula_arith_op_clses,
            *cls.formula_comp_op_clses,
            cls.text_cls,
        )
        return cls(value=cls.match_unserialize(kinds, val))


@dataclass
class LocalNode(BaseNode):
    "Local node"
    type = "local"
    value: ParameterNode

    @classmethod
    def parse_action(cls, toks: pp.ParseResults):
        "Parse action for the local node"
        return cls(
            value=ParameterNode(prm_name=toks.as_list()[0], prm_value=toks.as_list()[1])
        )

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().local

    def unparse(self) -> str:
        return " ".join([self.type, self.value.unparse()])

    def serialize(self) -> NodeSerialized:
        return [self.type, self.value.serialize()]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) != 2:
            raise ReconstructException("assert len == 2", data)
        typ, val = data
        if typ != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        return cls(value=cls.match_unserialize((ParameterNode,), val))


RootStatements = Union[FormulaNode, PrmNode, LocalNode, LineBreakNode, TextNode]


@dataclass
class RootNode(BaseNode):
    "Root node of AST"
    type = "topas"
    statements: list[RootStatements]

    @classmethod
    def parse_action(cls, toks: pp.ParseResults):
        "Parse action for the root node"
        stmts = toks.as_list()
        if len(stmts) and stmts[-1] == LineBreakNode():
            stmts = stmts[:-1]
        inst = cls(statements=[])
        # concat text nodes
        for stmt in stmts:
            last_stmt = inst.statements[-1] if inst.statements else None
            if isinstance(last_stmt, TextNode) and isinstance(stmt, TextNode):
                last_stmt.value = f"{last_stmt.value} {stmt.value}"
            else:
                inst.statements.append(stmt)

        return inst

    @classmethod
    def get_parser(cls):
        return cls.get_grammar().root

    @classmethod
    @property
    def root_statement_clses(cls) -> tuple[type[RootStatements], ...]:
        "Root node statement classes"
        return (
            cls.line_break_cls,
            cls.formula_cls,
            cls.prm_cls,
            cls.local_cls,
            cls.text_cls,
        )

    @classmethod
    def parse(cls, text, parse_all=True, print_dump=False) -> Self | TextNode:
        "Try to parse text with optional fallback"
        result = super().parse(text, parse_all=parse_all, print_dump=print_dump)
        return result  # type: ignore[assignment]

    def unparse(self):
        return " ".join(x.unparse() for x in self.statements)

    def serialize(self) -> NodeSerialized:
        return [self.type, *[x.serialize() for x in self.statements]]

    @classmethod
    def unserialize(cls, data: list[Any]):
        if not hasattr(data, "__len__") or len(data) < 1:
            raise ReconstructException("assert len >= 1", data)
        if data[0] != cls.type:
            raise ReconstructException(f"assert data[0] == {cls.type}", data)
        return cls(
            statements=[
                cls.match_unserialize(cls.root_statement_clses, x) for x in data[1:]
            ]
        )
