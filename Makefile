.PHONY: doctor test policy-check command-check run

AGENT ?= ./scripts/agent
PYTHON ?= ./.venv/bin/python
MESSAGE ?=

doctor:
	$(AGENT) doctor

test:
	$(PYTHON) -m pytest -q

policy-check:
	$(PYTHON) -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy(); print('startup policy ok')"
	$(PYTHON) -m agent.safety.validation config/capabilities.yaml

command-check:
	$(AGENT) commands validate

run:
	@if [ -z "$(MESSAGE)" ]; then echo 'Usage: make run MESSAGE="Explain RCS vs iMessage"'; exit 2; fi
	$(AGENT) --no-tools "$(MESSAGE)"
