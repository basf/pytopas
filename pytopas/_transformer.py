"Parser transformer"

from functools import partial
from typing import Any, List, Optional, Type

from pytopas.lark_standalone import Meta, Token, Transformer

from .token import AllTokens, BaseToken
from .tree import (
    AllTrees,
    FormulaTree,
    ParameterEquationTree,
    ParameterValueTree,
    TOPASTree,
    TopasTree,
)


def load_tree(data: str, children: Any):
    "Load tree of some type"
    for tree_class in AllTrees:
        if tree_class.data != data:
            continue
        return tree_class.from_children(children)
    raise AssertionError(f"{data!r} is unknown rule name")


def load_token(token: Token) -> BaseToken:
    "Load token of some type"
    for token_class in AllTokens:
        if token_class.type != token.type:
            continue
        return token_class.from_token(token)
    raise AssertionError(f"{token.type!r} is unknown token type")


class TOPASTransformer(Transformer):
    "Transform a generic tree and tokens to the specialized tree and tokens"

    def __default__(self, data, children, meta):
        "Default function that is called if there is no attribute matching data"
        try:
            return load_tree(data, children)
        except AssertionError:
            return TOPASTree(data, children, meta)

    def __default_token__(self, token):
        "Called if there is no attribute matching token type"
        return load_token(token)

    # __default_token__ not called in embedded transformer :(
    EQUALS = __default_token__
    SEMICOLON = __default_token__
    NAME = __default_token__
    OPERATOR = __default_token__
    PARAMETER_VAL = __default_token__
    XDD_FILENAME = __default_token__


def mk_tree_from_children_and_fold(tree_class: Type[TOPASTree], children):
    "Create tree from children and fold it"
    return tree_class.from_children(children).fold()


class TOPAS2CompactTransformer(Transformer):
    "Compact TOPAS tree"

    def __call_token_fold(self, tok: BaseToken):
        "Call fold() method of BaseToken"
        return tok.fold()

    # fold only some tokens:
    EQUALS = __call_token_fold
    SEMICOLON = __call_token_fold
    NAME = __call_token_fold
    OPERATOR = __call_token_fold
    PARAMETER_VAL = __call_token_fold

    # fold only some subtrees
    topas = partial(mk_tree_from_children_and_fold, TopasTree)
    parameter_value = partial(mk_tree_from_children_and_fold, ParameterValueTree)
    parameter_equation = partial(mk_tree_from_children_and_fold, ParameterEquationTree)
    formula = partial(mk_tree_from_children_and_fold, FormulaTree)


class Tree2TOPASTransformer(Transformer):
    "Fold TOPAS tree to source"

    def __default__(self, data, children, _):
        "Default function that is called if there is no attribute matching data"
        return load_tree(data, children).fold()

    def __default_token__(self, token):
        "Called if there is no attribute matching token type"
        return load_token(token).fold()


class TOPASTree2Tuples(Transformer):
    "TOPAS to tuples"

    def __default__(
        self, data: BaseToken, children: Optional[List], _: Optional[Meta] = None
    ):
        "Called if there is no attribute matching data"
        return (data, children)

    def __default_token__(self, token: BaseToken):
        "Called if there is no attribute matching token type"
        return token.serialize()
