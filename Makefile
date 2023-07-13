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

bump-patch: ## Bump the patch version (_._.X) everywhere it appears in the project
	@$(call i, Bumping the patch number)
	poetry run bumpversion patch --allow-dirty

bump-minor: ## Bump the minor version (_.X._) everywhere it appears in the project
	@$(call i, Bumping the minor number)
	poetry run bumpversion minor --allow-dirty

bump-major: ## Bump the major version (X._._) everywhere it appears in the project
	@$(call i, Bumping the major number)
	poetry run bumpversion major --allow-dirty

bump-release: ## Convert the version into a release variant (_._._) everywhere it appears in the project
	@$(call i, Removing the dev build suffix)
	poetry run bumpversion release --allow-dirty

bump-build: ## Bump the build number (_._._-____XX) everywhere it appears in the project
	@$(call i, Bumping the build number)
	poetry run bumpversion build --allow-dirty

format-fix:
	poetry run black --line-length 120 ${SRC_DIR}
	poetry run autoflake --in-place --remove-unused-variables $(PY_SOURCE)

setup:
	poetry install

test:
	@echo "Using: " $(WHYLABS_API_KEY)
	poetry run pytest

help: ## Show this help message.
	@echo 'usage: make [target] ...'
	@echo
	@echo 'targets:'
	@egrep '^(.+)\:(.*) ##\ (.+)' ${MAKEFILE_LIST} | sed -s 's/:\(.*\)##/: ##/' | column -t -c 2 -s ':#'
