# Makefile for Profile README
# Author: Juan Moisés de la Serna Tuya | ORCID: https://orcid.org/0000-0002-8401-8018

.PHONY: all install validate cite clean help

all: help

## Install dependencies
install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found"

## Validate dataset structure
validate:
	@echo "Validating dataset..."
	@python -c "import json; json.load(open('datapackage.json'))" && echo "✅ datapackage.json valid"
	@python -c "import json; json.load(open('codemeta.json'))" && echo "✅ codemeta.json valid"
	@python -c "import json; json.load(open('.zenodo.json'))" && echo "✅ .zenodo.json valid"
	@echo "✅ Validation complete"

## Show citation
cite:
	@echo "=== Citation ==="
	@cat CITATION.cff

## Check all required files exist
check:
	@for f in README.md LICENSE CITATION.cff codemeta.json AUTHORS.md .zenodo.json; do \
	  [ -f "$$f" ] && echo "✅ $$f" || echo "❌ $$f missing"; \
	done

## Clean cache files
clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean done"

## Show help
help:
	@echo "Available targets:"
	@echo "  make install   - Install dependencies"
	@echo "  make validate  - Validate JSON metadata files"
	@echo "  make cite      - Show citation information"
	@echo "  make check     - Check required files exist"
	@echo "  make clean     - Remove cache files"
