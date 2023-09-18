"Test tokens"
import pytest

from pytopas.token import BaseToken, XddFilenameToken


@pytest.mark.parametrize(
    "in_str, out_str",
    [
        ("some/path/file.name", "some/path/file.name"),
        ('"some/path/file.name"', "some/path/file.name"),
        ('"so me/pa th/file.name"', "so me/pa th/file.name"),
    ],
)
def test_xdd_filename_from_token(in_str: str, out_str: str):
    "Test xdd filename from token"

    in_token = BaseToken("XDD_FILENAME", in_str)
    out_token = XddFilenameToken.from_token(in_token)

    assert out_token.value == out_str


serialize_params = [
    ("some/path/file.name", "some/path/file.name"),
    ('"some/path/file.name"', "some/path/file.name"),
    ('"so me/pa th/file.name"', "'so me/pa th/file.name'"),
]


@pytest.mark.parametrize("in_str, out_str", serialize_params)
def test_xdd_filename_fold(in_str: str, out_str: str):
    "Test xdd filename fold()"

    in_token = BaseToken("XDD_FILENAME", in_str)
    out_token = XddFilenameToken.from_token(in_token)

    assert out_token.fold() == out_str


@pytest.mark.parametrize("in_str, out_str", serialize_params)
def test_xdd_filename_serialize(in_str: str, out_str: str):
    "Test xdd filename serialize()"

    in_token = BaseToken("XDD_FILENAME", in_str)
    out_token = XddFilenameToken.from_token(in_token)

    assert out_token.serialize() == (XddFilenameToken.type, out_str)
