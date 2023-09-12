"Command line tools"

import argparse
from io import TextIOWrapper
from json import JSONDecodeError

from .lark_standalone import UnexpectedToken
from .parser import TOPASParser
from .tree import TOPASParseTree


def topas2json():
    "CLI tool that converts TOPAS to JSON"
    arg_parser = argparse.ArgumentParser(
        prog="topas2json",
        description="Parse TOPAS input and output JSON",
    )
    arg_parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        help="Path to TOPAS file or '-' for stdin input",
    )
    arg_parser.add_argument(
        "-c", "--compact", action="store_true", help="Use compact output"
    )
    args = arg_parser.parse_args()

    file: TextIOWrapper = args.file
    input_topas = file.read()
    file.close()

    print("\n=== input topas source:\n", input_topas)

    parser = TOPASParser()

    try:
        tree = parser.parse(input_topas)
        print("\n=== original tree:\n", tree)
        print("\n=== original tree pretty:\n", tree.pretty())
        print("\n=== result json:\n", tree.to_json(compact=args.compact))
    except UnexpectedToken as e:
        print(e.state.value_stack)
        raise e


def json2topas():
    "CLI tool that converts JSON to TOPAS"
    arg_parser = argparse.ArgumentParser(
        prog="json2topas",
        description="Parse JSON input and output TOPAS",
    )
    arg_parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        help="Path to JSON file or '-' for stdin input",
    )
    args = arg_parser.parse_args()

    file: TextIOWrapper = args.file
    input_json = file.read()
    file.close()

    print("\n=== input json source:\n", input_json)
    try:
        tree = TOPASParseTree.from_json(input_json)
        print("\n=== original tree:\n", tree)
        print("\n=== original tree pretty:\n", tree.pretty())
        print("\n=== result topas:\n", tree.to_topas())
    except JSONDecodeError as e:
        raise e
    except UnexpectedToken as e:
        print(e.state.value_stack)
        raise e
