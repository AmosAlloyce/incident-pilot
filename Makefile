PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
PIP    := .venv/bin/pip

.PHONY: install seed run test

install:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

seed:
	PYTHONPATH=src $(PYTHON) -m incident_pilot.db.seed

run:
	@if [ -z "$(TICKET)" ]; then \
		echo "Usage: make run TICKET=\"describe the issue here\""; \
		exit 1; \
	fi
	PYTHONPATH=src $(PYTHON) -m incident_pilot.main --ticket "$(TICKET)"

test:
	PYTHONPATH=src $(PYTEST) tests/ -v
