"""Monthly ingestion of NYC TLC trip files into the raw zone."""

from datetime import UTC, datetime, timedelta

from airflow.sdk import Param, dag, get_current_context, task
from airflow.sdk.exceptions import AirflowFailException


@dag(
    dag_id="tlc_monthly_ingestion",
    schedule="@monthly",
    start_date=datetime(2024, 1, 1, tzinfo=UTC),
    end_date=datetime(2025, 12, 31, tzinfo=UTC),
    catchup=False,
    max_active_runs=2,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
    },
    params={
        "year_month": Param(
            None,
            type=["null", "string"],
            description="Month to load as YYYY-MM. "
            "Required for manual runs; leave empty otherwise.",
        ),
    },
    tags=["ingestion", "tlc"],
)
def tlc_monthly_ingestion():
    @task
    def ingest_month(dataset: str) -> str:
        from dataclasses import replace

        from nyc_mobility.config import Settings
        from nyc_mobility.ingestion.main import run
        from nyc_mobility.ingestion.scheduling import resolve_year_month

        context = get_current_context()
        try:
            year_month = resolve_year_month(
                context["params"].get("year_month"),
                context.get("data_interval_start"),
            )
        except ValueError as err:
            # Bad input: retrying cannot fix it, so fail now without retries.
            raise AirflowFailException(str(err)) from err

        settings = replace(Settings.from_env(), tlc_dataset=dataset, tlc_month=year_month)
        run(settings)  # network/storage errors here are normal exceptions → retried
        return year_month

    ingest_month("yellow_tripdata")


tlc_monthly_ingestion_dag = tlc_monthly_ingestion()
