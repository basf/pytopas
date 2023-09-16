"Test transformers"

import pytest

from pytopas.token import BaseToken
from pytopas.transformer import load_token


def test_load_token_error():
    "Test unknown token error"

    token = BaseToken("uNkNoWn", "")
    with pytest.raises(AssertionError):
        load_token(token)
