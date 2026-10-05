import os
from datetime import datetime, timezone

import psycopg


def get_connection_string() -> str:
    # Optional settings: sensible defaults are fine
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")

    # Required settings: crash immediately with a clear error if missing
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    database = os.environ["POSTGRES_DB"]

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def main() -> None:
    env = os.getenv("PIPELINE_ENV", "local")
    started_at = datetime.now(timezone.utc)

    with psycopg.connect(get_connection_string()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id     SERIAL PRIMARY KEY,
                env        TEXT        NOT NULL,
                started_at TIMESTAMPTZ NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO pipeline_runs (env, started_at) VALUES (%s, %s)",
            (env, started_at),
        )
        total_runs = conn.execute("SELECT count(*) FROM pipeline_runs").fetchone()[0]

    print(f"Recorded run in env={env} at {started_at.isoformat()}. Total runs: {total_runs}")


if __name__ == "__main__":
    main()