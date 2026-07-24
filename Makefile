# Canonical local and CI validation gate.

.PHONY: ci lint lint-spine test

ci: lint test lint-spine

lint:
	bash -n install.sh uninstall.sh skills/saga/saga-lint/scripts/run.sh skills/compat/saga-lint/scripts/run.sh
	node --check bin/saga-statusline.js
	ruff check bin/saga-project bin/saga-lint bin/saga-migrate bin/saga-skill-install tests

lint-spine:
	@if [ -d .planning ]; then ./bin/saga-lint .; fi

test:
	pytest -n auto -q tests
