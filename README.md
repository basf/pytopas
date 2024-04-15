# pytopas

This is an early version of Bruker's TOPAS macro language parser, used by [commercial](https://www.bruker.com/de/products-and-solutions/diffractometers-and-x-ray-microscopes/x-ray-diffractometers/diffrac-suite-software.html) and [academic](http://www.topas-academic.net) TOPAS code. We have compared two canonical parsing approaches for Python, `lark` vs. `pyparsing`, and ended up with `pyparsing` being more convenient for debugging.


## Installation

`pip install .`

Install package with optional dependencies with `pip install -e .[lint,test,release]`


## Usage

Parse a TOPAS macro language node with:

```sh
echo "xdd { 42 }" | topas2json - | json2topas -
```

More specifically, parse TOPAS input and convert it to JSON with:

```python
import json
from pytopas import TOPASParser

src = "a(b,c)"

tree = TOPASParser.parse(src)
print(json.dumps(tree))
```

Convert parser's JSON-encoded TOPAS code back into the TOPAS input format:

```python
import json
from pytopas import TOPASParseTree

input_json = """
["topas",
  ["formula",
    ["func_call", "a",
      ["formula", ["p", {"n": ["parameter_name", "b"]}]],
      ["formula", ["p", {"n": ["parameter_name", "c"]}]]]]]
"""
serialized = json.loads(input_json)
src = TOPASParser.reconstruct(serialized)
print(src)

```


## CLI

After installing the package, two command line utilities will be available.

```
usage: topas2json [-h] [--ignore-warnings] file

Parse TOPAS input and output JSON

positional arguments:
  file               Path to TOPAS file or '-' for stdin input

options:
  -h, --help         show this help message and exit
  --ignore-warnings  Don't print parsing warnings
```

```
usage: json2topas [-h] file

Parse JSON input and output TOPAS

positional arguments:
  file        Path to JSON file or '-' for stdin input

options:
  -h, --help  show this help message and exit

```


## License

Author Sergey Korolev, Tilde Materials Informatics

Copyright 2023 BASF SE

BSD 3-Clause
