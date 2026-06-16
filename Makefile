PYTHON ?= .venv/bin/python3
PIP ?= .venv/bin/pip

.PHONY: setup test

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -q
