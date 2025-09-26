SERVICE_NAME = mange-ta-main-front
COMPOSE_FILE = compose.yaml
PROD_COMPOSE_FILE = compose-prod-override.yaml

# lint:
# 	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) ruff check --fix /app/service /app/tests

# format:
# 	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uvx black /app/service /app/tests
# 	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uvx isort /app/service /app/tests
# 	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) uvx autopep8 --in-place --recursive /app/service /app/tests

# check-types:
# 	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) pyright /app/service /app/tests

# test:
# 	docker compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) pytest /app/tests

# lint-all: lint format check-types

# build-dev:
# 	docker compose -f $(COMPOSE_FILE) build $(SERVICE_NAME)

# build-prod:
# 	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) build $(SERVICE_NAME)

service-dev-up:
	docker compose -f $(COMPOSE_FILE) up --build

service-prod-up:
	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) up -d --build

service-stop:
	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) down --remove-orphans

service-clean:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f