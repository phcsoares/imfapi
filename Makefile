.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

ifneq (,$(wildcard ./.env))  # loads .env variables
    include .env
    export
endif

help:  ## show help message
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -fr .pytest_cache

format: ## formats code with ruff
	@uvx ruff format .

lint: ## check style with ruff
	@uvx ruff check .

lint-fix: ## check style with ruff and fix errors
	@uvx ruff check --fix .

pre-commit: ## runs pre-commit
	@ uv run pre-commit run --all-files

test: ## run tests quickly with the default Python
	@uv run pytest -vv --cov=src/imfapi --cov-report=term-missing

build: clean ## builds source and wheel package
	@uv build

publish: build			## publish new version to PyPI
	@uv publish --token=$(UV_PUBLISH_TOKEN)
