SERVICE_NAME = mange-ta-main
COMPOSE_FILE = compose.yaml
PROD_COMPOSE_FILE = compose-prod-override.yaml

service-dev-up:
	docker compose -f $(COMPOSE_FILE) up --build

service-prod-up:
	DOCKER_BUILDKIT=0 docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) up -d --build

service-stop:
	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) down --remove-orphans

service-clean:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f

clean:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f