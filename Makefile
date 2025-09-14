.PHONY: help install test clean

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up files"

install:
	python3 -m pip install -r requirements.txt
	npm install -g @supabase/mcp-server-supabase

test:
	./scripts/run-tests.sh

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .pytest_cache
