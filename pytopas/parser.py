"TOPAS parser"

from dataclasses import dataclass
from functools import cache, reduce
from typing import Any, List, Union, Type

import pyparsing as pp

from .base import BaseNode, FallbackNode, FormulaNode

RootStatements = Union[FormulaNode, FallbackNode]
root_statements_cls = (FormulaNode, FallbackNode)


@dataclass
class RootNode(BaseNode):
    "Root node of AST"
    type = "topas"
    statements: List[RootStatements]

    @classmethod
    @cache
    def get_parser(cls):
        root_stmts = [
            x.get_parser()
            for x in root_statements_cls
            if not isinstance(x, FallbackNode)
        ]
        root_stmt = reduce(lambda a, b: a | b, root_stmts).set_results_name("stmt")
        parser = (
            pp.MatchFirst([root_stmt, FallbackNode.get_parser()])[...]
            .set_results_name("stmts")
            .add_parse_action(lambda toks: cls(statements=toks.as_list()))
        )
        return parser

    def unparse(self):
        return " ".join(x.unparse() for x in self.statements)

    def serialize(self):
        return [self.type, *[x.serialize() for x in self.statements]]

    @classmethod
    def unserialize(cls, data: list[Any]):
        assert len(data) >= 1
        assert data[0] == cls.type
        return cls(
            statements=[cls.match_unserialize(root_statements_cls, x) for x in data[1:]]
        )
