SERVICE_NAME = mange-ta-main-back
COMPOSE_FILE = compose-backend.yaml
PROD_COMPOSE_FILE = compose-backend-prod-override.yaml

lint:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) ruff check /app/service /app/tests

lint-fix:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) ruff check --fix /app/service /app/tests

format:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uvx isort /app/service /app/tests
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uvx black /app/service /app/tests
	
check-types:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) pyright /app/service /app/tests

lint-all: lint check-types

test:
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) coverage run -m pytest /app/tests && \
	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) coverage report -m
	
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