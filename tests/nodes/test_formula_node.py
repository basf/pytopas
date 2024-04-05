"Test FormulaNode and operations"

import json
from pathlib import Path

import pytest

from pytopas import ast
from pytopas.exc import ReconstructException

OPS_DIR = Path(__file__).parent / "formula_op"
FORMULA_DIR = Path(__file__).parent / "formula"


def get_opts_params():
    ins = list(sorted(OPS_DIR.glob("*.in.inp")))
    jsons = sorted(OPS_DIR.glob("*.json"))
    outs = sorted(OPS_DIR.glob("*.out.inp"))
    result = []
    for row in zip(ins, jsons, outs):
        parts = row[0].name.split(".")
        result.append([parts[0], parts[1], *row])
    return result


@pytest.mark.parametrize(
    "in_cls_name, out_cls_name, in_path, json_path, out_path", get_opts_params()
)
def test_formula_op_node(
    in_cls_name: str, out_cls_name: str, in_path: Path, json_path: Path, out_path: Path
):
    "Test FormulsOps"
    cls_in = getattr(ast, in_cls_name)
    assert cls_in, "cls_in exists"
    cls_out = getattr(ast, out_cls_name)
    assert cls_out, "cls_out exists"
    text_in = in_path.read_text()[:-1]
    serialized = json.loads(json_path.read_text())
    text_out = out_path.read_text()[:-1]

    node = cls_in.parse(text_in, parse_all=True)
    assert isinstance(node, cls_out)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_formula_unary_op_unserialize_fail():
    "Test FormulaUnaryPlus and descendants"
    with pytest.raises(ReconstructException):
        ast.FormulaUnaryPlus.unserialize([])
    with pytest.raises(ReconstructException):
        ast.FormulaUnaryPlus.unserialize(["not this node", 1])


def test_formula_binary_op_unserialize_fail():
    "Test FormulaAdd and descendants"
    with pytest.raises(ReconstructException):
        ast.FormulaAdd.unserialize([])
    with pytest.raises(ReconstructException):
        ast.FormulaAdd.unserialize(["not this node", 1, 1])


def get_formula_params():
    ins = list(sorted(FORMULA_DIR.glob("*.in.inp")))
    jsons = sorted(FORMULA_DIR.glob("*.json"))
    outs = sorted(FORMULA_DIR.glob("*.out.inp"))
    return zip(ins, jsons, outs)


@pytest.mark.parametrize("in_path, json_path, out_path", get_formula_params())
def test_formula_node(in_path: Path, json_path: Path, out_path: Path):
    "Test FormulsNode"
    text_in = in_path.read_text()[:-1]
    serialized = json.loads(json_path.read_text())
    text_out = out_path.read_text()[:-1]

    node = ast.FormulaNode.parse(text_in, parse_all=True)
    assert isinstance(node, ast.FormulaNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


def test_formula_unserialize_fail():
    "Test FormulaNode"
    with pytest.raises(ReconstructException):
        ast.FormulaNode.unserialize([])
    with pytest.raises(ReconstructException):
        ast.FormulaNode.unserialize(["not this node", 1])
