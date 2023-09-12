"TOPAS parser"

from typing import Callable, Optional

from .lark_standalone import DATA, MEMO, Lark, UnexpectedInput
from .transformer import TOPASTransformer
from .tree import TOPASParseTree


class TOPASParser(Lark):
    "TOPAS parser"

    def __init__(self) -> None:
        "Init"
        self._load(
            {"data": DATA, "memo": MEMO},
            transformer=TOPASTransformer(),
        )

    def parse(
        self,
        text: str,
        start: Optional[str] = None,
        on_error: Optional[Callable[[UnexpectedInput], bool]] = None,
    ) -> TOPASParseTree:
        "Parse TOPAS"

        return super().parse(text, start, on_error)
