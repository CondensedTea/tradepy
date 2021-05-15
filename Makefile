TESTS = tests

VENV ?= .venv
CODE = tests tradepy tools
CREATE_DB = tools.create_db
RATE_MUTATOR = tools.rate_mutator
BOT = tools.trade_bot

.PHONY: venv
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

.PHONY: test
test:
	$(VENV)/bin/pytest -v tests

.PHONY: lint
lint:
	$(VENV)/bin/flake8 --jobs 4 --statistics --show-source $(CODE)
	$(VENV)/bin/pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(VENV)/bin/mypy $(CODE)
	$(VENV)/bin/black --skip-string-normalization --check $(CODE)

.PHONY: format
format:
	$(VENV)/bin/isort $(CODE)
	$(VENV)/bin/black --skip-string-normalization $(CODE)
	$(VENV)/bin/autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(VENV)/bin/unify --in-place --recursive $(CODE)

.PHONY: ci
ci:	lint test

.PHONY: db
db:
	$(VENV)/bin/python -m $(CREATE_DB)

.PHONY: up
up:
	$(VENV)/bin/python -m $(RATE_MUTATOR) & export FLASK_APP=tradepy; $(VENV)/bin/flask run

.PHONE: bot
bot:
	$(VENV)/bin/python -m $(BOT)