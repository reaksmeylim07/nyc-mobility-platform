import os
import re

import requests

TLC_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def parse_year_month(year_month: str) -> tuple[str, str]:
    """Split 'YYYY-MM' into ('YYYY', 'MM'). Raise ValueError if the format is invalid."""
    match = re.fullmatch(r"\d{4}-\d{2}", year_month)
    if not match:
        raise ValueError(f"Invalid year_month {year_month!r}, expected 'YYYY-MM'")

    year, month = year_month.split("-")

    if not (1 <= int(month) <= 12):
        raise ValueError(f"Invalid Month: {month}, expected 01 to 12")
    return year, month


# ---------- naming ----------


def build_object_key(dataset: str, year_month: str) -> str:
    """Build the raw-zone object key for one monthly TLC file.

    Example:
        build_object_key("yellow_tripdata", "2024-01")
        -> "raw/yellow_tripdata/year=2024/month=01/yellow_tripdata_2024-01.parquet"
    """
    year, month = parse_year_month(year_month)
    return f"raw/{dataset}/year={year}/month={month}/{dataset}_{year_month}.parquet"


def build_source_url(dataset: str, year_month: str) -> str:
    return f"{TLC_BASE_URL}/{dataset}_{year_month}.parquet"


# ---------- download ----------


def download_file(url: str, dest_path: str) -> int:
    """Stream a file from a URL to disk. Returns the size in bytes."""
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()  # crash on 403/404/500
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB at a time
                f.write(chunk)
    return os.path.getsize(dest_path)


def source_file_exists(url: str, timeout: int = 30) -> bool:
    """Check whether the provider has published a file, without downloading it.

    Returns True for 200, False for 403/404 (not published yet),
    and raises for any other error status so retries can handle it.
    """
    response = requests.head(url, timeout=timeout, allow_redirects=True)

    if response.status_code == 200:
        return True
    if response.status_code in (403, 404):
        return False
    else:
        response.raise_for_status()
        return False
