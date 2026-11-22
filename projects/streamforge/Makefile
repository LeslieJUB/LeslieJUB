.PHONY: up down logs producer test lint
up:
	docker compose up --build -d
down:
	docker compose down
logs:
	docker compose logs -f worker api
producer:
	docker compose run --rm producer
test:
	pytest
lint:
	ruff check .
