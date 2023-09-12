.DEFAULT_GOAL := parser
.PHONY: parser

pytopas/lark_standalone.py: pytopas/grammar.lark
	PYTHONHASHSEED=0 python -m lark.tools.standalone -c -s topas $< > $@

parser: pytopas/lark_standalone.py

dist: pytopas/* pyproject.toml
	flit build
