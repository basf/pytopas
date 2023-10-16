# pytopas

This is the parser for Bruker's TOPAS macro language. We have compared two canonical parsing approaches for Python: `lark` vs. `pyparsing`.

## Usage

Parse TOPAS input and convert it to JSON:

```python
from pytopas import TOPASParser

src = "a = a + 1 ; 0"

parser = TOPASParser()
tree = parser.parse(src)
print(tree.to_json(compact=True))
```

Convert parser's JSON-encoded TOPAS code back into the TOPAS input format:

```python
from pytopas import TOPASParseTree

input_json = '["topas", ["a = a + 1 ; 0"]]'

tree = TOPASParseTree.from_json(input_json)
print(tree.to_topas())

```

## Command line utilities

After installing the package, two command line utilities will be available.

```
usage: topas2json [-h] [-c] file

Parse TOPAS input and output JSON

positional arguments:
  file           Path to TOPAS file or '-' for stdin input

options:
  -h, --help     show this help message and exit
  -c, --compact  Use compact output
```

```
usage: json2topas [-h] file

Parse JSON input and output TOPAS

positional arguments:
  file        Path to JSON file or '-' for stdin input

options:
  -h, --help  show this help message and exit

```

## Development

Install package with optional dependencies: `pip install -e .[dev,lint,test,release]`

Regenerate standalone `lark` parser after `grammar.lark` change: `make parser`

## License

Author Sergey Korolev, Tilde Materials Informatics

Copyright 2023 BASF SE

BSD 3-Clause
