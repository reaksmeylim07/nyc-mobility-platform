.PHONY: up down reset run logs psql

up:        ## Start all services in the background
	docker compose up -d --build

down:      ## Stop services (keeps data)
	docker compose down

reset:     ## Stop services AND delete all data
	docker compose down -v

run:       ## Run the ingestion job once
	docker compose run --rm ingestion

logs:      ## Follow logs from all services
	docker compose logs -f

psql:      ## Open a SQL shell inside Postgres
	docker compose exec postgres psql -U nyc -d nyc_mobility