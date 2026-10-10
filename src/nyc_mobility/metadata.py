from datetime import datetime, timezone

import psycopg






def record_load(dsn:str,dataset: str, year_month: str, object_key: str, size_bytes: int) -> None:
    with psycopg.connect(dsn) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_file_loads (
                load_id     SERIAL PRIMARY KEY,
                dataset     TEXT        NOT NULL,
                year_month  TEXT        NOT NULL,
                object_key  TEXT        NOT NULL,
                size_bytes  BIGINT      NOT NULL,
                loaded_at   TIMESTAMPTZ NOT NULL,

                CONSTRAINT uq_raw_file_loads_object_key UNIQUE (object_key)
            )
            """
        )
        conn.execute(
            """
            INSERT INTO raw_file_loads (dataset, year_month, object_key, size_bytes, loaded_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (object_key) 
            DO UPDATE SET
                dataset    = EXCLUDED.dataset,
                year_month = EXCLUDED.year_month,
                size_bytes = EXCLUDED.size_bytes,
                loaded_at  = EXCLUDED.loaded_at
            WHERE EXCLUDED.loaded_at > raw_file_loads.loaded_at;
            """,
            (dataset, year_month, object_key, size_bytes, datetime.now(timezone.utc)),
        )