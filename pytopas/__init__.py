import sys
from pathlib import Path

from pytopas.lark_standalone import Lark_StandAlone, Transformer, Token, UnexpectedToken

__VERSION__ = "0.0.1"

class TOPASTransformer(Transformer):
    "TOPAS parser transformer"

    def XDD_FILENAME(self, tok: Token):
        "Parse file path"
        if tok.startswith('"') and tok.endswith('"'):
            tok.update(value=tok.value.strip('"'))
        return tok


parser = Lark_StandAlone(transformer=TOPASTransformer())

with Path(sys.argv[1]).open() as f:
    INPUT = f.read()

try:
    tree = parser.parse(INPUT)
    print(tree)
    print(tree.pretty())
except UnexpectedToken as e:
    print(e.state.value_stack)
    raise e
