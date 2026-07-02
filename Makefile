PYTHON ?= .venv/bin/python3
PIP ?= .venv/bin/pip
RETENTION_DAYS ?= 30

.PHONY: setup test cleanup

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -q

cleanup:
	RETENTION_DAYS=$(RETENTION_DAYS) bash scripts/cleanup-old-runs.sh

cleanup-dry-run:
	RETENTION_DAYS=$(RETENTION_DAYS) DRY_RUN=true bash scripts/cleanup-old-runs.sh
