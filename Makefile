.PHONY: help install run test lint docker-build docker-run

help:
	@echo "Common targets:"
	@echo "  make install      Install Python deps"
	@echo "  make run          Run API locally on :8080"
	@echo "  make test         Run unit tests"
	@echo "  make lint         Run ruff lint"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container on :8080"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8080

test:
	pytest -q

lint:
	ruff check . || true

docker-build:
	docker build -t mediflow:latest .

docker-run:
	docker run --rm -p 8080:8080 --env-file .env mediflow:latest

