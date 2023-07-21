import sys
from pathlib import Path

from lark import Lark, Token, Transformer, UnexpectedToken


class TOPASTransformer(Transformer):
    "TOPAS parser transformer"

    def XDD_FILENAME(self, tok: Token):
        "Parse file path"
        if tok.startswith('"') and tok.endswith('"'):
            tok.update(value=tok.value.strip('"'))
        return tok


with (Path(__file__).parent / "grammar.lark").open() as f:
    parser = Lark(
        f.read(), start="program", parser="lalr", transformer=TOPASTransformer()
    )

with Path(sys.argv[1]).open() as f:
    INPUT = f.read()

try:
    tree = parser.parse(INPUT)
    print(tree)
    print(tree.pretty())
except UnexpectedToken as e:
    print(e.state.value_stack)
    raise e
