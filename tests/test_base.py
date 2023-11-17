"Test base nodes"

from dataclasses import asdict, dataclass
import pytest
import pyparsing as pp
from pytopas.exc import ParseException, ParseWarning
from pytopas.base import (
    BaseNode,
    DepsMixin,
    FallbackNode,
    ParameterNameNode,
    ParameterValueNode,
    FormulaNode,
    FormulaElementNode,
    FormulaUnaryPlus,
    FormulaUnaryMinus,
    FormulaAdd,
    FormulaSub,
    FormulaMul,
    FormulaDiv,
    FormulaExp,
    FormulaEQ,
    FormulaNE,
    FormulaLT,
    FormulaLE,
    FormulaGE,
    FormulaGT,
)


def test_fallback_node():
    "Test FallbackNode"
    text = "some random text"
    with pytest.warns(ParseWarning):
        node = FallbackNode.parse(text)
    assert node.value == text.split(" ")[0]
    assert node.unparse() == text.split(" ")[0]
    serialized = node.serialize()
    assert serialized == [node.type, text.split(" ")[0]]
    assert FallbackNode.unserialize(serialized) == node

    with pytest.warns(ParseWarning):
        fallback_node = ParameterValueNode.parse(text)
        assert isinstance(fallback_node, FallbackNode)
    assert fallback_node == node

    with pytest.raises(ParseException):
        ParameterValueNode.parse(text, permissive=False)


def test_parameter_name_node():
    "Test ParameterNameNode"
    text_in = "P_name1"
    node = ParameterNameNode.parse(text_in, permissive=True)
    assert isinstance(node, ParameterNameNode)
    assert node.unparse() == text_in
    serialized = node.serialize()
    assert serialized == [node.type, text_in]
    assert ParameterNameNode.unserialize(serialized) == node


@pytest.mark.parametrize(
    "text_in, as_dict, text_out",
    [
        (
            "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
            {
                "value": -12.3,
                "esd": 2,
                "backtick": True,
                "lim_min": -13,
                "lim_max": 2.1,
            },
            "-12.3`_2_LIMIT_MIN_-13_LIMIT_MAX_2.1",
        ),
        (
            "10_LIMIT_MAX_20_LIMIT_MIN_5",
            {
                "value": 10,
                "esd": None,
                "backtick": False,
                "lim_min": 5,
                "lim_max": 20,
            },
            "10_LIMIT_MIN_5_LIMIT_MAX_20",
        ),
    ],
)
def test_parameter_value_node(text_in, as_dict, text_out):
    "Test ParameterValueNode"
    node = ParameterValueNode.parse(text_in, permissive=False)
    assert isinstance(node, ParameterValueNode)
    assert asdict(node) == as_dict
    assert node.unparse() == text_out
    serialized = node.serialize()
    assert serialized == [node.type, text_out]
    assert ParameterValueNode.unserialize(serialized) == node


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "1",
            ["formula_element", 1],
            "1",
        )
    ],
)
def test_formula_el_node(text_in: str, serialized, text_out):
    "Test FormulaElementNode and co"
    node = FormulaElementNode.parse(text_in, permissive=False)
    assert isinstance(node, FormulaElementNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@dataclass
class DummyTestNode(BaseNode):
    type = "test"

    @classmethod
    def get_parser(cls, permissive=True):
        parser = pp.Literal("TEST").add_parse_action(lambda toks: cls())
        return cls._wrap_fallback(parser) if permissive else parser

    def unparse(self):
        return "TEST"

    def serialize(self):
        return [self.type]

    @classmethod
    def unserialize(cls, data):
        assert len(data) == 1
        assert data[0] == cls.type
        return cls()


class DepsFormulaOverrides(DepsMixin):
    @classmethod
    @property
    def formula_element_cls(cls):
        return DummyTestNode

    @classmethod
    @property
    def formula_unary_plus_cls(cls):
        return FormulaUnaryPlusTest

    @classmethod
    @property
    def formula_unary_minus_cls(cls):
        return FormulaUnaryMinusTest

    @classmethod
    @property
    def formula_add_cls(cls):
        return FormulaAddTest

    @classmethod
    @property
    def formula_sub_cls(cls):
        return FormulaSubTest

    @classmethod
    @property
    def formula_mul_cls(cls):
        return FormulaMulTest

    @classmethod
    @property
    def formula_div_cls(cls):
        return FormulaDivTest

    @classmethod
    @property
    def formula_exp_cls(cls):
        return FormulaExpTest

    @classmethod
    @property
    def formula_eq_cls(cls):
        return FormulaEQTest

    @classmethod
    @property
    def formula_ne_cls(cls):
        return FormulaNETest

    @classmethod
    @property
    def formula_le_cls(cls):
        return FormulaLETest

    @classmethod
    @property
    def formula_lt_cls(cls):
        return FormulaLTTest

    @classmethod
    @property
    def formula_ge_cls(cls):
        return FormulaGETest

    @classmethod
    @property
    def formula_gt_cls(cls):
        return FormulaGTTest


@dataclass
class FormulaUnaryPlusTest(FormulaUnaryPlus, DepsFormulaOverrides):
    pass


@dataclass
class FormulaUnaryMinusTest(FormulaUnaryMinus, DepsFormulaOverrides):
    pass


@dataclass
class FormulaAddTest(FormulaAdd, DepsFormulaOverrides):
    pass


@dataclass
class FormulaSubTest(FormulaSub, DepsFormulaOverrides):
    pass


@dataclass
class FormulaMulTest(FormulaMul, DepsFormulaOverrides):
    pass


@dataclass
class FormulaDivTest(FormulaDiv, DepsFormulaOverrides):
    pass


@dataclass
class FormulaExpTest(FormulaExp, DepsFormulaOverrides):
    pass


@dataclass
class FormulaEQTest(FormulaEQ, DepsFormulaOverrides):
    pass


@dataclass
class FormulaNETest(FormulaNE, DepsFormulaOverrides):
    pass


@dataclass
class FormulaLETest(FormulaLE, DepsFormulaOverrides):
    pass


@dataclass
class FormulaLTTest(FormulaLT, DepsFormulaOverrides):
    pass


@dataclass
class FormulaGETest(FormulaGE, DepsFormulaOverrides):
    pass


@dataclass
class FormulaGTTest(FormulaGT, DepsFormulaOverrides):
    pass


@pytest.mark.parametrize(
    "cls_in, cls_out, text_in, serialized, text_out",
    [
        (FormulaUnaryPlusTest, DummyTestNode, "+ TEST", ["test"], "TEST"),
        (
            FormulaUnaryMinusTest,
            FormulaUnaryMinusTest,
            "- TEST",
            ["-1", ["test"]],
            "- TEST",
        ),
        (
            FormulaAddTest,
            FormulaAddTest,
            "TEST+TEST",
            ["+", ["test"], ["test"]],
            "TEST + TEST",
        ),
        (
            FormulaSubTest,
            FormulaSubTest,
            "TEST-TEST",
            ["-", ["test"], ["test"]],
            "TEST - TEST",
        ),
        (
            FormulaMulTest,
            FormulaMulTest,
            "TEST*TEST",
            ["*", ["test"], ["test"]],
            "TEST * TEST",
        ),
        (
            FormulaDivTest,
            FormulaDivTest,
            "TEST/TEST",
            ["/", ["test"], ["test"]],
            "TEST / TEST",
        ),
        (
            FormulaExpTest,
            FormulaExpTest,
            "TEST^TEST",
            ["^", ["test"], ["test"]],
            "TEST ^ TEST",
        ),
        (
            FormulaEQTest,
            FormulaEQTest,
            "TEST==TEST",
            ["==", ["test"], ["test"]],
            "TEST == TEST",
        ),
        (
            FormulaNETest,
            FormulaNETest,
            "TEST!=TEST",
            ["!=", ["test"], ["test"]],
            "TEST != TEST",
        ),
        (
            FormulaLETest,
            FormulaLETest,
            "TEST<TEST",
            ["<", ["test"], ["test"]],
            "TEST < TEST",
        ),
        (
            FormulaLTTest,
            FormulaLTTest,
            "TEST<=TEST",
            ["<=", ["test"], ["test"]],
            "TEST <= TEST",
        ),
        (
            FormulaGETest,
            FormulaGETest,
            "TEST>TEST",
            [">", ["test"], ["test"]],
            "TEST > TEST",
        ),
        (
            FormulaGTTest,
            FormulaGTTest,
            "TEST>=TEST",
            [">=", ["test"], ["test"]],
            "TEST >= TEST",
        ),
    ],
)
def test_formula_op_nodes(cls_in, cls_out, text_in: str, serialized, text_out):
    "Test FormulaOp and co"
    node = cls_in.parse(text_in, permissive=False, parse_all=True)
    assert isinstance(node, cls_out)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@dataclass
class FormulaTestNode(FormulaNode, DepsFormulaOverrides):
    pass


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "TEST",
            ["formula", ["test"]],
            "TEST",
        ),
        # arith operations
        (
            "+TEST",
            ["formula", ["test"]],
            "TEST",
        ),
        (
            "-TEST",
            ["formula", ["-1", ["test"]]],
            "- TEST",
        ),
        (
            "TEST+TEST+TEST+TEST",
            ["formula", ["+", ["test"], ["test"], ["test"], ["test"]]],
            "TEST + TEST + TEST + TEST",
        ),
        (
            "TEST-TEST-TEST-TEST",
            ["formula", ["-", ["test"], ["test"], ["test"], ["test"]]],
            "TEST - TEST - TEST - TEST",
        ),
        (
            "TEST*TEST*TEST*TEST",
            ["formula", ["*", ["test"], ["test"], ["test"], ["test"]]],
            "TEST * TEST * TEST * TEST",
        ),
        (
            "TEST/TEST/TEST/TEST",
            ["formula", ["/", ["test"], ["test"], ["test"], ["test"]]],
            "TEST / TEST / TEST / TEST",
        ),
        (
            "TEST^TEST^TEST^TEST",
            ["formula", ["^", ["test"], ["test"], ["test"], ["test"]]],
            "TEST ^ TEST ^ TEST ^ TEST",
        ),
        (
            "TEST+(TEST-TEST)*TEST/TEST^(TEST+TEST)",
            [
                "formula",
                [
                    "+",
                    ["test"],
                    [
                        "/",
                        ["*", ["-", ["test"], ["test"]], ["test"]],
                        ["^", ["test"], ["+", ["test"], ["test"]]],
                    ],
                ],
            ],
            "TEST + ( TEST - TEST ) * TEST / TEST ^ ( TEST + TEST )",
        ),
        # comparison operations
        (
            "TEST==TEST",
            ["formula", ["==", ["test"], ["test"]]],
            "TEST == TEST",
        ),
        (
            "TEST!=TEST",
            ["formula", ["!=", ["test"], ["test"]]],
            "TEST != TEST",
        ),
        (
            "TEST<TEST",
            ["formula", ["<", ["test"], ["test"]]],
            "TEST < TEST",
        ),
        (
            "TEST<=TEST",
            ["formula", ["<=", ["test"], ["test"]]],
            "TEST <= TEST",
        ),
        (
            "TEST>TEST",
            ["formula", [">", ["test"], ["test"]]],
            "TEST > TEST",
        ),
        (
            "TEST>=TEST",
            ["formula", [">=", ["test"], ["test"]]],
            "TEST >= TEST",
        ),
    ],
)
def test_formula_node(text_in: str, serialized, text_out):
    "Test FormulaNode and co"
    node = FormulaTestNode.parse(text_in, permissive=False, parse_all=True)
    assert isinstance(node, FormulaTestNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out


@pytest.mark.parametrize(
    "text_in, serialized, text_out",
    [
        (
            "1+(2-3)*4/5^(6+7)",
            [
                "formula",
                [
                    "+",
                    ["formula_element", 1],
                    [
                        "/",
                        [
                            "*",
                            ["-", ["formula_element", 2], ["formula_element", 3]],
                            ["formula_element", 4],
                        ],
                        [
                            "^",
                            ["formula_element", 5],
                            ["+", ["formula_element", 6], ["formula_element", 7]],
                        ],
                    ],
                ],
            ],
            "1 + ( 2 - 3 ) * 4 / 5 ^ ( 6 + 7 )",
        ),
        (
            "1== 2!=3 <4<= 5>6 >=7",
            [
                "formula",
                [
                    ">=",
                    [
                        ">",
                        [
                            "<=",
                            [
                                "<",
                                [
                                    "!=",
                                    [
                                        "==",
                                        ["formula_element", 1],
                                        ["formula_element", 2],
                                    ],
                                    ["formula_element", 3],
                                ],
                                ["formula_element", 4],
                            ],
                            ["formula_element", 5],
                        ],
                        ["formula_element", 6],
                    ],
                    ["formula_element", 7],
                ],
            ],
            "1 == 2 != 3 < 4 <= 5 > 6 >= 7",
        ),
    ],
)
def test_formula_real_node(text_in: str, serialized, text_out):
    "Test FormulaNode and co"
    node = FormulaNode.parse(text_in, permissive=False, parse_all=True)
    assert isinstance(node, FormulaNode)
    assert node.serialize() == serialized
    reconstructed = node.unserialize(serialized)
    assert reconstructed == node
    assert reconstructed.unparse() == text_out
