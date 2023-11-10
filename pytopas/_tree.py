"Enchanced Tree"
# pylint: disable=import-outside-toplevel

import json
from typing import Any, List, Sequence, Tuple, Type, Union, cast

from .lark_standalone import Tree, _Leaf_T
from .token import AllTokens, BaseToken


class TOPASTree(Tree[_Leaf_T]):
    "Enchanced Tree"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data!r}, {self.children!r})"

    @classmethod
    def from_tree(cls, tree):
        "Create tree from another tree"
        return cls(tree.data, tree.children, tree.meta)

    @classmethod
    def from_children(cls, children):
        "Create tree from children"
        assert cls.data
        return cls(cls.data, children)

    def serialize(self, compact: bool = False) -> Tuple[str, Any]:
        "Serialize Tree to nested tuples"
        from pytopas.transformer import TOPAS2CompactTransformer, TOPASTree2Tuples

        tree = self
        if compact:
            tree = TOPAS2CompactTransformer().transform(tree)
        if tree.data != "topas":
            tree = TopasTree.from_children([tree])

        # join strings
        if isinstance(tree.children, list) and all(
            isinstance(x, str) for x in tree.children
        ):
            tree = tree.__class__.from_children(
                [" ".join(cast(List[str], tree.children))]
            )
        return TOPASTree2Tuples().transform(tree)

    def fold(self) -> str:
        "Maybe convert to string"
        assert isinstance(self.children, list) and all(
            isinstance(x, str) for x in self.children
        ), "Can fold only if all tree's children are strings"
        return " ".join(cast(List[str], self.children))

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
    def _from_str(cls, data: str) -> "TOPASTree[_Leaf_T]":
        "Private helper"
        from .parser import TOPASParser

        tree = TOPASParser().parse(data)
        return cast(TOPASTree[_Leaf_T], tree)

    @classmethod
    def _from_tuples(
        cls, data: Union[Tuple[str, Any], str]
    ) -> "Union[TOPASTree[_Leaf_T], BaseToken]":
        "Private helper"
        if isinstance(data, str):
            return cls._from_str(data)

        assert type(data) in [list, tuple]
        assert len(data) == 2

        head, tail = data
        assert type(tail) in [str, tuple, list]

        # token
        if isinstance(tail, str):
            for token_class in AllTokens:
                if token_class.type != head:
                    continue
                return token_class(head, tail)
            raise AssertionError(f"{head!r} is unknown token type")

        # tree
        for tree_class in AllTrees:
            if tree_class.data != head:
                continue
            return tree_class.from_children(
                [x if isinstance(x, str) else cls._from_tuples(x) for x in tail]
            )
        raise AssertionError(f"{head!r} is unknown rule name")

    @classmethod
    def from_tuples(cls, data: Tuple[str, Any]) -> "TOPASTree[_Leaf_T]":
        "Convert tuples to Tree"
        assert type(data) in [list, tuple]
        assert len(data) == 2

        head, tail = data
        assert head == "topas"
        assert type(tail) in [tuple, list]

        if len(tail) == 1 and isinstance(tail[0], str):
            return cls._from_str(tail[0])

        children = [cls._from_tuples(x) for x in tail]
        return TopasTree.from_children(children)

    @classmethod
    def from_json(cls, data: str) -> "TOPASTree[_Leaf_T] | BaseToken":
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


TOPASParseTree = TOPASTree[BaseToken]

AllTrees: Sequence[Type[TOPASTree]] = [
    TopasTree,
    ParameterValueTree,
    FormulaTree,
    ParameterEquationTree,
]
