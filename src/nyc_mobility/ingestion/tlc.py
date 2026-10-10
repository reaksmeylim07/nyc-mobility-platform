import os


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


def build_source_url(dataset: str, year_month: str) -> str:
    return f"{TLC_BASE_URL}/{dataset}_{year_month}.parquet"

# ---------- download ----------

def download_file(url: str, dest_path: str) -> int:
    """Stream a file from a URL to disk. Returns the size in bytes."""
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()               # crash on 403/404/500
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):   # 1 MB at a time
                f.write(chunk)
    return os.path.getsize(dest_path)
