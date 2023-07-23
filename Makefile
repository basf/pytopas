.DEFAULT_GOAL := parser
.PHONY: parser

pytopas/lark_standalone.py: pytopas/grammar.lark
	python -m lark.tools.standalone -c -s program $< > $@

parser: pytopas/lark_standalone.py

dist: pytopas/* pyproject.toml
	flit build
