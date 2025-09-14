# MCP Server Setup - Makefile

.PHONY: help install test clean check

help: ## Show this help message
	@echo "MCP Server Setup - Available Commands"
	@echo "====================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "Installing dependencies..."
	python3 -m pip install -r requirements.txt
	npm install -g @supabase/mcp-server-supabase

test: ## Run test suite
	@echo "Running tests..."
	./scripts/run-tests.sh

clean: ## Clean up temporary files
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache

check: ## Check system requirements
	@echo "Checking system requirements..."
	@echo "Node.js version: $$(node -v)"
	@echo "Python version: $$(python3 --version)"
	@echo "Docker version: $$(docker --version)"
	@echo "Docker Compose version: $$(docker-compose --version)"
	@echo "MCP server installed: $$(npx @supabase/mcp-server-supabase --version 2>/dev/null || echo 'Not installed')"
