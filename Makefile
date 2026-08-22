PYTHON ?= .venv/bin/python3
PIP ?= .venv/bin/pip
RETENTION_DAYS ?= 30

.PHONY: setup test lint doctor cleanup

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -q

lint:
	PYTHON_BIN=$(PYTHON) bash scripts/lint.sh

doctor:
	PYTHON_BIN=$(PYTHON) bash scripts/workspace-doctor.sh --fetch

cleanup:
	RETENTION_DAYS=$(RETENTION_DAYS) bash scripts/cleanup-old-runs.sh

cleanup-dry-run:
	RETENTION_DAYS=$(RETENTION_DAYS) DRY_RUN=true bash scripts/cleanup-old-runs.sh
