-include .env

SHELL = /bin/bash

clean_mypy:
	rm -rf .mypy_cache

clean_ruff:
	rm -rf .ruff_cache

clean: clean_mypy clean_ruff

mypy:
	uv run mypy . --ignore-missing-imports --check-untyped-defs

ruff:
	uv run ruff format .
	uv run ruff check . --fix

sync:
	uv sync --all-extras
