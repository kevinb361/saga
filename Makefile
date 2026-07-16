# Canonical local and CI validation gate.

.PHONY: ci lint lint-spine test

ci: lint test lint-spine

lint:
	bash -n install.sh uninstall.sh
	node --check bin/saga-statusline.js
	ruff check bin/saga-project bin/saga-lint tests

lint-spine:
	@if [ -d .planning ]; then ./bin/saga-lint .; fi

test:
	pytest -n auto -q tests
