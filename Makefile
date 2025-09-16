.PHONY: help install start stop clean logs

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make start    - Start MAREA application"
	@echo "  make stop     - Stop MAREA application"
	@echo "  make logs     - Show container logs"
	@echo "  make clean    - Clean up files"

install:
	pip install -r requirements.txt

start:
	docker compose up --build -d

stop:
	docker compose down

logs:
	docker compose logs -f

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .pytest_cache
