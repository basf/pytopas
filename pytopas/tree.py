"Enchanced Tree"

import json
from typing import Any, Generic, List, Sequence, Tuple, Type, cast

from .lark_standalone import Token, Tree, _Leaf_T
from .token import AllTokens, BaseToken


class TOPASTree(Tree[Generic[_Leaf_T]]):
    "Enchanced Tree"

    def __repr__(self):
        return "{}({!r}, {!r})".format(self.__class__.__name__, self.data, self.children)

    @classmethod
    def from_tree(cls, tree):
        return cls(tree.data, tree.children, tree.meta)

    @classmethod
    def from_children(cls, children):
        assert cls.data
        return cls(cls.data, children)

    def serialize(self, compact: bool = False) -> Tuple[str, Any]:
        "Serialize Tree to nested tuples"
        from .transformer import TOPAS2CompactTransformer, TOPASTree2Tuples

        tree = self
        if compact:
            tree = TOPAS2CompactTransformer().transform(tree)
            print("\n=== compact tree:\n", tree)
            if hasattr(tree, "pretty"):
                print("\n=== compact tree pretty:\n", tree.pretty())
        return TOPASTree2Tuples().transform(tree)

    def fold(self) -> str:
        "Maybe convert to string"
        if isinstance(self.children, str):
            return self.children

        assert isinstance(self.children, list) and all(
            [type(x) == str for x in self.children]
        ), "Can fold only if all tree's children are strings"
        return " ".join(cast("List[str]", self.children))

    def to_json(self, compact: bool = False) -> str:
        "Convert Tree to JSON"

        return json.dumps(
            self.serialize(compact=compact), indent=None if compact else 2
        )

    def to_topas(self) -> str:
        "Convert Tree to TOPAS source code"
        from .transformer import Tree2TOPASTransformer

        folded = Tree2TOPASTransformer().transform(self)
        return " ".join(folded.children)

    @classmethod
    def from_tuples(cls, data: Tuple[str, Any]) -> "TOPASTree | BaseToken":
        "Convert tuples to Tree"

        assert type(data) in [list, tuple]
        assert len(data) == 2

        head, tail = data

        assert type(tail) in [str, tuple, list]

        # token
        if type(tail) == str:
            for token_class in AllTokens:
                if token_class.type != head:
                    continue
                return token_class(head, tail)
            raise AssertionError(f'{head!r} is unknown token type')

        # tree
        for tree_class in AllTrees:
            if tree_class.data != head:
                continue
            return tree_class.from_children(
                [x if type(x) == str else cls.from_tuples(x) for x in tail]
            )
        raise AssertionError(f'{head!r} is unknown rule name')

    @classmethod
    def from_json(cls, data: str) -> "TOPASTree | BaseToken":
        "Convert JSON to Tree"
        return cls.from_tuples(json.loads(data))


class TopasTree(TOPASTree):
    "topas tree"
    data = "topas"

    def fold(self):
        "Don't fold"
        return self


class ParameterValueTree(TOPASTree):
    "parameter_value tree"
    data = "parameter_value"


class FormulaTree(TOPASTree):
    "formula tree"
    data = "formula"


class ParameterEquationTree(TOPASTree):
    "parameter_equation tree"
    data = "parameter_equation"


TOPASParseTree = TOPASTree[Token]

AllTrees: Sequence[Type[TOPASTree]] = [
    TopasTree,
    ParameterValueTree,
    FormulaTree,
    ParameterEquationTree,
]
