# Project settings
PACKAGE := some_dags
PACKAGES := $(PACKAGE) tests
MODULES := $(wildcard $(PACKAGE)/*.py)

# const
.DEFAULT_GOAL := help
FAILURES := .pytest_cache/v/cache/lastfailed
DIST_FILES := dist/*.tar.gz dist/*.whl

# MAIN TASKS ##################################################################

.PHONY: all
all: install


.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# PROJECT DEPENDENCIES ########################################################

install: .install .cache ## Install project dependencies

GIT_DIR = .git
.install: poetry.lock
	poetry install
	poetry check
	@touch $@

poetry.lock: pyproject.toml
	poetry lock
	@touch $@

.cache:
	@mkdir -p .cache

requirements.txt: poetry.lock ## Generate requirements.txt
	@poetry export --without-hashes -f requirements.txt > requirements.txt

# CHECKS ######################################################################

.PHONY: check
check: install   ## Run linters and static analysis
	poetry run isort $(PACKAGES)
	poetry run black $(PACKAGES)
	poetry run flakehell lint $(PACKAGE)
# poetry run mypy --show-error-codes --ignore-missing-imports --config-file pyproject.toml $(PACKAGE)


# TESTS #######################################################################

.PHONY: test
test: install ## Run unit tests
	@if test -e $(FAILURES); then poetry run pytest tests --last-failed --exitfirst; fi
	@rm -rf $(FAILURES)
	poetry run pytest
