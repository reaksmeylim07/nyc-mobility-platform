import pytest

from nyc_mobility.ingestion.tlc import build_object_key, build_source_url


def test_build_source_url_uses_provider_flat_naming():
    assert build_source_url("yellow_tripdata", "2024-01") == (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
    )


def test_build_object_key_uses_hive_partitions():
    assert build_object_key("yellow_tripdata", "2024-01") == (
        "raw/yellow_tripdata/year=2024/month=01/yellow_tripdata_2024-01.parquet"
    )


@pytest.mark.parametrize(
    "dataset, year_month, expected",
    [
        (
            "green_tripdata",
            "2023-12",
            "raw/green_tripdata/year=2023/month=12/green_tripdata_2023-12.parquet",
        ),
        (
            "fhv_tripdata",
            "2019-02",
            "raw/fhv_tripdata/year=2019/month=02/fhv_tripdata_2019-02.parquet",
        ),
    ],
)
def test_build_object_key_for_other_datasets(dataset, year_month, expected):
    assert build_object_key(dataset, year_month) == expected


@pytest.mark.parametrize("bad_value", ["2024-1", "2024-13", "24-01", "2024/01", ""])
def test_build_object_key_rejects_invalid_year_month(bad_value):
    with pytest.raises(ValueError):
        build_object_key("yellow_tripdata", bad_value)