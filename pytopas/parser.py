"TOPAS parser"

from dataclasses import dataclass
from functools import cache, reduce
from typing import Any, List, Type, Union

import pyparsing as pp

from .base import BaseNode, FallbackNode, FormulaNode, NodeSerialized, LineBreakNode
from .exc import ReconstructException

RootStatements = Union[FormulaNode, LineBreakNode, FallbackNode]


@dataclass
class RootNode(BaseNode):
    "Root node of AST"
    type = "topas"
    statements: List[RootStatements]

    @classmethod
    @property
    def root_statement_clses(cls) -> tuple[Type[RootStatements], ...]:
        return (cls.line_break_cls, cls.formula_cls, cls.fallback_cls)

    @classmethod
    @cache
    def get_parser(cls, permissive=True):
        def action(toks: pp.ParseResults):
            stmts = toks.as_list()
            if len(stmts) and stmts[-1] == LineBreakNode():
                stmts = stmts[:-1]
            return cls(statements=stmts)

        root_stmts = pp.MatchFirst(
            [
                x.get_parser(permissive)
                for x in cls.root_statement_clses
                if x != cls.fallback_cls
            ]
        ).set_results_name("stmt")
        parser = pp.OneOrMore(root_stmts).add_parse_action(action)
        return parser

    @classmethod
    def parse(cls, text, permissive=True, parse_all=True):
        "Try to parse text with optional fallback"
        return super().parse(text, permissive, parse_all=parse_all)

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


class Parser:
    "TOPAS Parser"

    @staticmethod
    def parse(text: str, permissive=True) -> NodeSerialized:
        "Parse TOPAS source code to serialized tree"

        tree = RootNode.parse(text, permissive=True)
        return tree.serialize()

    @staticmethod
    def reconstruct(data: list[Any]) -> str:
        "Reconstruct TOPAS source code from setialized tree"
        tree = RootNode.unserialize(data)
        return tree.unparse()
