SERVICE_NAME = mange-ta-main-back
COMPOSE_FILE = compose-backend.yaml
PROD_COMPOSE_FILE = compose-backend-prod-override.yaml

lint:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uv run ruff check /app/service /app/tests

lint-fix:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uv run ruff check --fix /app/service /app/tests

format:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uvx isort /app/service /app/tests
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uvx black /app/service /app/tests

check-types:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uv run pyright /app/service /app/tests

test:
	rm -f .coverage .coverage* || true
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uv run coverage run -m pytest /app/tests
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uv run coverage report -m

lint-all: lint format check-types

build-dev:
	docker compose -f $(COMPOSE_FILE) build $(SERVICE_NAME) --no-cache

build-prod:
	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) build $(SERVICE_NAME) --no-cache

dev-up:
	docker compose -f $(COMPOSE_FILE) up --build

prod-up:
	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) up -d --build

stop:
	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) down --remove-orphans

clean:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f
