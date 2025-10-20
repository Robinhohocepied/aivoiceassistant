.PHONY: help venv ensure-env install run test lint docker-build docker-run start

# Configurable vars
PYTHON ?= python3
VENV ?= .venv
VENV_PY := $(VENV)/bin/python
PORT ?= 8080

help:
	@echo "Common targets:"
	@echo "  make start        Create venv, install deps, run app"
	@echo "  make venv         Create virtualenv in $(VENV)"
	@echo "  make install      Install Python deps into venv"
	@echo "  make run          Run API locally on :$(PORT)"
	@echo "  make test         Run unit tests"
	@echo "  make lint         Run ruff lint (if installed)"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container on :8080"
	@echo "\nOverrides: make PYTHON=python3.11 start"

venv:
	@[ -d "$(VENV)" ] || $(PYTHON) -m venv $(VENV)

ensure-env:
	@[ -f .env ] || ( [ -f .env.example ] && cp .env.example .env || true )

install: venv
	$(VENV_PY) -m pip install -U pip
	$(VENV_PY) -m pip install -r requirements.txt

run:
	$(VENV_PY) -m uvicorn app.main:app --reload --port $(PORT)

test:
	$(VENV_PY) -m pytest -q

lint:
	@if [ -x "$(VENV)/bin/ruff" ]; then \
		$(VENV)/bin/ruff check . ; \
	else \
		echo "ruff not installed (optional)." ; \
	fi

docker-build:
	docker build -t mediflow:latest .

docker-run:
	docker run --rm -p 8080:8080 --env-file .env mediflow:latest

start: ensure-env install
	@echo "Starting API on :$(PORT)"
	$(VENV_PY) -m uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload
