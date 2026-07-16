# Canonical local and CI validation gate.

.PHONY: ci lint test

ci: lint test

lint:
	bash -n install.sh uninstall.sh
	node --check bin/saga-statusline.js
	ruff check bin/saga-project tests

test:
	pytest -n auto -q tests
