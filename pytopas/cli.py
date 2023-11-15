"Command line tools"

import argparse
import json
import sys
from io import TextIOWrapper
from typing import List, Optional

from .parser import Parser


def _topas2json_parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    "Parse topas2json args"

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
        "-p",
        "--permissive",
        action="store_true",
        help="Forgive parser errors",
        default=True,
    )
    return arg_parser.parse_args(args=args is not None and args or sys.argv[1:])


def topas2json(args: Optional[argparse.Namespace] = None):
    "CLI tool that converts TOPAS to JSON"

    args = args is not None and args or _topas2json_parse_args()
    file: TextIOWrapper = args.file
    input_topas = file.read()
    file.close()

    serialized = Parser.parse(input_topas, args.permissive)
    print(json.dumps(serialized))


def _json2topas_parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    "Parse json2topas args"
    arg_parser = argparse.ArgumentParser(
        prog="json2topas",
        description="Parse JSON input and output TOPAS",
    )
    arg_parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        help="Path to JSON file or '-' for stdin input",
    )
    return arg_parser.parse_args(args=args is not None and args or sys.argv[1:])


def json2topas(args: Optional[argparse.Namespace] = None):
    "CLI tool that converts JSON to TOPAS"

    args = args is not None and args or _json2topas_parse_args()
    file: TextIOWrapper = args.file
    input_json = file.read()
    file.close()

    try:
        src = Parser.reconstruct(json.loads(input_json))
        print(src)
    except json.JSONDecodeError as exp:
        raise exp
