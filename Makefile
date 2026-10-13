.PHONY: up down reset run logs psql test test-dags lint format up-airflow

up:        ## Start all services in the background
	docker compose up -d --build

up-airflow: ## Start the full stack including Airflow (UI: http://localhost:8080)
	docker compose --profile airflow up -d --build

down:      ## Stop services (keeps data)
	docker compose --profile airflow down

reset:     ## Stop services AND delete all data
	docker compose --profile airflow down -v

run:       ## Run the ingestion job once
	docker compose run --rm --build ingestion

logs:      ## Follow logs from all services
	docker compose logs -f

psql:      ## Open a SQL shell inside Postgres
	docker compose exec postgres psql -U nyc -d nyc_mobility

test:      ## Run the unit tests
	uv run pytest

test-dags: ## Run DAG integrity tests inside the Airflow image
	docker build -f docker/airflow/Dockerfile -t nyc-mobility-airflow:local .
	docker run --rm -v "$(CURDIR)":/repo -w /repo nyc-mobility-airflow:local \
		bash -c "pip install --quiet pytest && python -m pytest tests/dags -q -p no:cacheprovider"

lint:      ## Check code style and common bugs
	uv run ruff check .
	uv run ruff format --check .

format:    ## Auto-fix style issues
	uv run ruff check --fix .
	uv run ruff format .
