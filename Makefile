.PHONY: help venv ensure-env install run test lint docker-build docker-run start tunnel tunnel-url qa-verify qa-inbound agent-test qa-send

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
	@echo "  make tunnel       Start ngrok tunnel to :$(PORT) (requires ngrok)"
	@echo "  make tunnel-url   Print active ngrok https URL"
	@echo "  make qa-verify    Verify WhatsApp webhook via tunnel (needs WHATSAPP_VERIFY_TOKEN)"
	@echo "  make qa-inbound   Send sample inbound message via tunnel"
	@echo "  make agent-test   Quick OpenAI connectivity test"
	@echo "  make qa-send      Send a direct WhatsApp text via Graph API"
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

# --- Local tunneling & QA helpers ---
tunnel:
	@command -v ngrok >/dev/null 2>&1 || { echo "ngrok not installed. Install with: brew install ngrok && ngrok config add-authtoken <TOKEN>"; exit 1; }
	@echo "Starting ngrok tunnel to http://localhost:$(PORT) ..."
	ngrok http $(PORT)

tunnel-url:
	@$(PYTHON) - <<-'PY'
	import json, sys
	from urllib.request import urlopen
	try:
	    data = json.load(urlopen('http://127.0.0.1:4040/api/tunnels'))
	    urls = [t['public_url'] for t in data.get('tunnels', []) if t.get('public_url','').startswith('https://')]
	    if urls:
	        print(urls[0])
	    else:
	        sys.exit(1)
	except Exception:
	    sys.exit(1)
	PY

qa-verify:
	@WHATSAPP_VERIFY_TOKEN=$${WHATSAPP_VERIFY_TOKEN:?Set WHATSAPP_VERIFY_TOKEN in env or .env}; \
	TUNNEL="${TUNNEL}"; \
	if [ -z "$$TUNNEL" ]; then TUNNEL="$$( $(MAKE) -s tunnel-url 2>/dev/null || true )"; fi; \
	[ -n "$$TUNNEL" ] || { echo "No tunnel URL found. Start ngrok (make tunnel) or set TUNNEL=https://<domain>"; exit 1; }; \
	echo "Verifying webhook at $$TUNNEL/webhooks/whatsapp"; \
	curl -i "$$TUNNEL/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=$$WHATSAPP_VERIFY_TOKEN&hub.challenge=12345"

qa-inbound:
	@TUNNEL="${TUNNEL}"; \
	if [ -z "$$TUNNEL" ]; then TUNNEL="$$( $(MAKE) -s tunnel-url 2>/dev/null || true )"; fi; \
	[ -n "$$TUNNEL" ] || { echo "No tunnel URL found. Start ngrok (make tunnel) or set TUNNEL=https://<domain>"; exit 1; }; \
	echo "Posting sample inbound to $$TUNNEL/webhooks/whatsapp"; \
	curl -s -X POST "$$TUNNEL/webhooks/whatsapp" -H 'Content-Type: application/json' -d '{"entry":[{"changes":[{"value":{"metadata":{"phone_number_id":"PHONE_ID"},"contacts":[{"profile":{"name":"Alice"},"wa_id":"+32471123456"}],"messages":[{"from":"+32471123456","id":"wamid.ABC","timestamp":"1690000000","type":"text","text":{"body":"Bonjour"}}]}}]}]}' | cat

# Start Codex CLI with project .env loaded so MCP env is available
codex:
	@set -a; [ -f .env ] && . ./.env; set +a; codex

agent-test: install
	$(VENV_PY) -m agents.sanity_check

qa-send:
	@WHATSAPP_TOKEN=$${WHATSAPP_TOKEN:?Set WHATSAPP_TOKEN}; \
	WHATSAPP_PHONE_ID=$${WHATSAPP_PHONE_ID:?Set WHATSAPP_PHONE_ID}; \
	TO=$${TO:?Set recipient TO=E164digits}; \
	echo "Sending to $$TO via phone_id=$$WHATSAPP_PHONE_ID"; \
	curl -s -i -X POST "https://graph.facebook.com/v18.0/$$WHATSAPP_PHONE_ID/messages" \
		-H "Authorization: Bearer $$WHATSAPP_TOKEN" \
		-H "Content-Type: application/json" \
		-d '{"messaging_product":"whatsapp","to":"'"$$TO"'","type":"text","text":{"body":"Test from Mediflow (qa-send)"}}' | cat
