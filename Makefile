NAME=
PY_SOURCE=$(shell find whylabs_toolkit/ -type f -name "*.py")
SHA=$(shell git rev-parse HEAD)
VERSION=$(SHA)
REQUIREMENTS=requirements.txt
SRC_DIR=./whylabs_toolkit/

.PHONY: default 
.PHONY: lint format format-fix test setup help requirements

default:help

requirements: requirements.txt

requirements.txt: pyproject.toml
	poetry export -f requirements.txt > requirements.txt

lint:
	poetry run mypy ${SRC_DIR} --config-file=mypy.ini

format:
	poetry run black --check --line-length 120 ${SRC_DIR}
	poetry run autoflake --check --in-place --remove-unused-variables $(PY_SOURCE)

format-fix:
	poetry run black --line-length 120 ${SRC_DIR}
	poetry run autoflake --in-place --remove-unused-variables $(PY_SOURCE)

setup:
	poetry install

test:
	poetry run pytest

help: ## Show this help message.
	@echo 'usage: make [target] ...'
	@echo
	@echo 'targets:'
	@egrep '^(.+)\:(.*) ##\ (.+)' ${MAKEFILE_LIST} | sed -s 's/:\(.*\)##/: ##/' | column -t -c 2 -s ':#'
