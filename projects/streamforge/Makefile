.PHONY: up down logs producer spark test lint migrate

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f worker api

producer:
	docker compose run --rm producer --count 1000 --rate 100

spark:
	docker compose --profile spark run --rm spark-streaming

migrate:
	docker compose run --rm migrate

test:
	pytest -q

lint:
	ruff check --select E,F --ignore E501 .
