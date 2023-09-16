"Test base token"

from pytopas.token import BaseToken


def test_base_token_repr():
    "Test token __repr__"

    assert repr(BaseToken("type", "value")) == "BaseToken('type', 'value')"
