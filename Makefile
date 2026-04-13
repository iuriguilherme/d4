.PHONY: dev down migrate test test-api test-web lint

# Start all services
dev:
	docker-compose up --build

# Start in detached mode
dev-d:
	docker-compose up --build -d

# Stop all services
down:
	docker-compose down

# Run Alembic migrations
migrate:
	docker-compose exec api alembic upgrade head

# Run all tests
test: test-api test-web

# Run API tests
test-api:
	docker-compose exec api pytest api/tests/ -v

# Run web tests
test-web:
	docker-compose exec web pytest web/tests/ -v

# Lint
lint:
	docker-compose exec api ruff check api/
	docker-compose exec web ruff check web/

# Open a shell in the API container
api-shell:
	docker-compose exec api bash

# Open a shell in the web container
web-shell:
	docker-compose exec web bash

# Fresh start: remove volumes and rebuild
reset:
	docker-compose down -v
	docker-compose up --build
