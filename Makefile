.PHONY: up down reset run logs psql test lint format

up:        ## Start all services in the background
	docker compose up -d --build

down:      ## Stop services (keeps data)
	docker compose down

reset:     ## Stop services AND delete all data
	docker compose down -v

run:       ## Run the ingestion job once
	docker compose run --rm --build ingestion

logs:      ## Follow logs from all services
	docker compose logs -f

psql:      ## Open a SQL shell inside Postgres
	docker compose exec postgres psql -U nyc -d nyc_mobility

test:      ## Run the unit tests
	uv run pytest

lint:      ## Check code style and common bugs
	uv run ruff check .
	uv run ruff format --check .

format:    ## Auto-fix style issues
	uv run ruff check --fix .
	uv run ruff format .