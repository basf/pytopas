"Test base tree"

import pytest

from pytopas import TOPASParser
from pytopas.tree import TOPASParseTree, TOPASTree


def test_tree_base_repr():
    "Test tree __repr__"

    assert repr(TOPASTree("data", [])) == "TOPASTree('data', [])"


def test_tree_from_tree():
    "Test tree from_tree()"

    tree = TOPASParseTree("data", [], None)
    other = TOPASParseTree.from_tree(tree)
    assert tree.data == other.data
    assert tree.children == other.children
    assert tree.meta == other.meta


def test_tree_base_serialize_not_topas():
    "Test tree serialize() with wrong tree"
    tree = TOPASParseTree("data", [])
    assert tree.serialize() == ("topas", [("data", [])])


def test_tree_base_to_json():
    "Test tree to json"
    tree = TOPASParseTree("data", [])
    assert tree.to_json(compact=True) == '["topas", [["data", []]]]'


def test_tree_base_to_topas_str():
    "Test tree to topas when folded to str"

    tree = TOPASParser().parse("1")
    assert tree.to_topas() == "1"


def test_tree_base_from_tuples_str():
    "Test tree from tuples when input is str"

    tree = TOPASParseTree._from_tuples("1")  # pylint: disable=protected-access
    assert isinstance(tree, TOPASTree) and tree.data == "topas"


def test_tree_base_from_tuples_unknown_token():
    "Test tree from tuples when unknown token type"

    with pytest.raises(AssertionError):
        TOPASParseTree._from_tuples(("uNkNoWn", ""))  # pylint: disable=protected-access


def test_tree_base_from_tuples_unknown_rule():
    "Test tree from tuples when unknown tree type"

    with pytest.raises(AssertionError):
        TOPASParseTree._from_tuples(("uNkNoWn", []))  # pylint: disable=protected-access


def test_tree_base_from_json():
    "Test tree from json"

    TOPASParseTree.from_json('["topas", []]')
