# pytopas

Bruker's TOPAS macro language parser.

## Usage

Parse TOPAS source code and convert it to json:

```python
from pytopas import TOPASParser

src = "a = a + 1 ; 0"

parser = TOPASParser()
tree = parser.parse(src)
print(tree.to_json(compact=True))
```

Convert JSON encoded TOPAS code back into TOPAS source code:

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
