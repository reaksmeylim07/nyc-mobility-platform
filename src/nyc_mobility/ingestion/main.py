import os
import tempfile

from nyc_mobility.config import Settings
from nyc_mobility.ingestion.tlc import build_object_key, build_source_url, download_file
from nyc_mobility.metadata import record_load
from nyc_mobility.storage import ensure_bucket, get_s3_client


def run(settings: Settings) -> None:
    """Ingest one month of TLC data into the raw zone and record the load."""
    dataset, year_month = settings.tlc_dataset, settings.tlc_month

    url = build_source_url(dataset, year_month)
    object_key = build_object_key(dataset, year_month)

    s3 = get_s3_client(settings)
    ensure_bucket(s3, settings.s3_bucket)

    with tempfile.TemporaryDirectory() as tmp_dir:
        local_path = os.path.join(tmp_dir, os.path.basename(object_key))
        print(f"[{settings.pipeline_env}] Downloading {url}")
        size_bytes = download_file(url, local_path)
        print(f"Downloaded {size_bytes / 1_000_000:.1f} MB")

        s3.upload_file(local_path, settings.s3_bucket, object_key)
        print(f"Uploaded to s3://{settings.s3_bucket}/{object_key}")

    record_load(settings.postgres_dsn, dataset, year_month, object_key, size_bytes)
    print("Load recorded in Postgres.")


def main() -> None:
    run(Settings.from_env())


if __name__ == "__main__":
    main()