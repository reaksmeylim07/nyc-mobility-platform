import os
import tempfile
from datetime import datetime, timezone

import boto3
import psycopg
import requests

TLC_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


# ---------- naming ----------

def build_object_key(dataset: str, year_month: str) -> str:
    """Build the raw-zone object key for one monthly TLC file.

    Example:
        build_object_key("yellow_tripdata", "2024-01")
        -> "raw/yellow_tripdata/year=2024/month=01/yellow_tripdata_2024-01.parquet"
    """
    year, month = year_month.split("-")
    return f"raw/{dataset}/year={year}/month={month}/{dataset}_{year_month}.parquet"


# ---------- download ----------

def download_file(url: str, dest_path: str) -> int:
    """Stream a file from a URL to disk. Returns the size in bytes."""
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()               # crash on 403/404/500
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):   # 1 MB at a time
                f.write(chunk)
    return os.path.getsize(dest_path)


# ---------- object storage ----------

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT_URL"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name="us-east-1",                  # required by boto3; MinIO ignores it
    )


def ensure_bucket(s3, bucket: str) -> None:
    existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if bucket not in existing:
        s3.create_bucket(Bucket=bucket)
        print(f"Created bucket: {bucket}")


# ---------- metadata ----------

def get_connection_string() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    database = os.environ["POSTGRES_DB"]
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def record_load(dataset: str, year_month: str, object_key: str, size_bytes: int) -> None:
    with psycopg.connect(get_connection_string()) as conn:
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


# ---------- the job ----------

def main() -> None:
    dataset = os.getenv("TLC_DATASET", "yellow_tripdata")
    year_month = os.getenv("TLC_MONTH", "2024-01")
    bucket = os.environ["S3_BUCKET"]

    file_name = f"{dataset}_{year_month}.parquet"
    url = f"{TLC_BASE_URL}/{file_name}"
    object_key = build_object_key(dataset, year_month)

    s3 = get_s3_client()
    ensure_bucket(s3, bucket)

    with tempfile.TemporaryDirectory() as tmp_dir:          # deleted automatically afterwards
        local_path = os.path.join(tmp_dir, file_name)
        print(f"Downloading {url}")
        size_bytes = download_file(url, local_path)
        print(f"Downloaded {size_bytes / 1_000_000:.1f} MB")

        s3.upload_file(local_path, bucket, object_key)
        print(f"Uploaded to s3://{bucket}/{object_key}")

    record_load(dataset, year_month, object_key, size_bytes)
    print("Load recorded in Postgres.")


if __name__ == "__main__":
    main()