PORT ?= 8080
UVICORN ?= uvicorn
NGROK ?= ngrok
NGROK_DOMAIN ?=

.PHONY: run test lint format install tunnel

run:
	$(UVICORN) app.main:app --reload --port $(PORT)

test:
	pytest -q

lint:
	ruff check .

format:
	ruff --fix .

install:
	pip install -r requirements.txt

tunnel:
	@command -v $(NGROK) >/dev/null 2>&1 || { echo "ngrok not found. Install via 'brew install ngrok' or https://ngrok.com/download"; exit 1; }
	@if [ -n "$(NGROK_DOMAIN)" ]; then \
		$(NGROK) http --domain $(NGROK_DOMAIN) $(PORT); \
	else \
		$(NGROK) http $(PORT); \
	fi
