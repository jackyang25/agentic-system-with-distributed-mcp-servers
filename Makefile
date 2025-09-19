.PHONY: help install start stop clean logs test-planner

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make start    - Start MAREA application"
	@echo "  make stop     - Stop MAREA application"
	@echo "  make logs     - Show container logs"
	@echo "  make test-planner - Run planner agent test in container"
	@echo "  make clean    - Clean up files"

install:
	pip install -r requirements.txt

start:
	docker compose up --build -d

stop:
	docker compose down

logs:
	docker compose logs -f

test-planner:
	docker exec marea-main python tests/test_planner_agent.py

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .pytest_cache
