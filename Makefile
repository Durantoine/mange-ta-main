SERVICE_NAME = mange_ta_main
COMPOSE_FILE = compose.yaml
PROD_COMPOSE_FILE = compose-prod-override.yaml

service-dev-up:
	docker compose -f $(COMPOSE_FILE) build --no-cache
	docker compose -f $(COMPOSE_FILE) up

service-prod-up:
	DOCKER_BUILDKIT=0 docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) up -d --build

stop:
	docker compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) down --remove-orphans

clean:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans
	docker system prune -f

docs:
	python -m pip install -r docs/requirements.txt
	make -C docs html
	
