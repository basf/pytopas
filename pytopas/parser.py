"TOPAS parser"

from typing import Any, List

from .ast import NodeSerialized, RootNode


class Parser:
    "TOPAS Parser"

    @staticmethod
    def parse(text: str) -> NodeSerialized:
        "Parse TOPAS source code to serialized tree"
        tree = RootNode.parse(text)
        return tree.serialize()

    @staticmethod
    def reconstruct(data: List[Any]) -> str:
        "Reconstruct TOPAS source code from setialized tree"
        tree = RootNode.unserialize(data)
        return tree.unparse()
