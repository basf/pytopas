"Test TOPAS parser"

from pytopas.parser import Parser


def test_parser():
    "Test Parser"
    serialized = Parser.parse("1")
    assert serialized == ["topas", ["formula", ["p", {"v": ["parameter_value", "1"]}]]]
    src = Parser.reconstruct(serialized)
    assert src == "1"
