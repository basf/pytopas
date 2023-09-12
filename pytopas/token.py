"Parser tokens"

import shlex
from typing import Any, Sequence, Tuple, Type

from pytopas.lark_standalone import Token


class BaseToken(Token):
    "Base token class"

    type: str = "__OVERRIDE_ME__"

    def __repr__(self):
        return "{}({!r}, {!r})".format(self.__class__.__name__, self.type, self.value)

    @classmethod
    def from_token(cls, tok: Token):
        "Instantiate from Token"
        if cls.type != "base":
            assert tok.type == cls.type
        return cls(tok.type, tok.value)

    def serialize(self) -> Tuple[str, Any]:
        "Serialize to tuple"
        return (self.type, self.value)

    def fold(self) -> str | Tuple[str, Any]:
        "Maybe serialize to string"
        return self.value


class EqualsToken(BaseToken):
    "EQUALS token class"
    type = "EQUALS"


class SemicolonToken(BaseToken):
    "SEMICOLON token class"
    type = "SEMICOLON"


class NameToken(BaseToken):
    "NAME token class"
    type = "NAME"


class ParameterValToken(BaseToken):
    "PARAMETER_VAL token class"
    type = "PARAMETER_VAL"


class OperatorToken(BaseToken):
    "OPERATOR token class"
    type = "OPERATOR"


class XddFilenameToken(BaseToken):
    "XDD_FILENAME token class"
    type = "XDD_FILENAME"

    @classmethod
    def from_token(cls, tok: Token):
        "Instantiate from Token"

        return cls(
            tok.type,
            # handle quoted path
            tok.value.removeprefix('"').removesuffix('"')
            if tok.startswith('"') and tok.endswith('"')
            else tok.value,
        )

    def fold(self):
        "Quote path"
        return shlex.quote(self.value)

    def serialize(self) -> Tuple[str, Any]:
        "Serialize to tuple"
        return (self.type, self.fold())


AllTokens: Sequence[Type[BaseToken]] = [
    EqualsToken,
    SemicolonToken,
    NameToken,
    ParameterValToken,
    OperatorToken,
    XddFilenameToken,
]
