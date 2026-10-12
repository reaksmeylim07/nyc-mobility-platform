"""Monthly ingestion of NYC TLC trip files into the raw zone."""

from datetime import UTC, datetime, timedelta

from airflow.sdk import dag, get_current_context, task


@dag(
    dag_id="tlc_monthly_ingestion",
    schedule="@monthly",
    start_date=datetime(2024, 1, 1, tzinfo=UTC),
    end_date=datetime(2025, 12, 31, tzinfo=UTC),  # historical loader (see note below)
    catchup=False,
    max_active_runs=2,  # at most 2 months in parallel
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
    },
    tags=["ingestion", "tlc"],
)
def tlc_monthly_ingestion():
    @task
    def ingest_month(dataset: str) -> str:
        # Imports INSIDE the task: the DAG processor re-reads this file constantly,
        # so we keep the top of the file light.
        from dataclasses import replace

        from nyc_mobility.config import Settings
        from nyc_mobility.ingestion.main import run

        context = get_current_context()
        year_month = context["data_interval_start"].strftime("%Y-%m")

        settings = replace(Settings.from_env(), tlc_dataset=dataset, tlc_month=year_month)
        run(settings)
        return year_month

    ingest_month("yellow_tripdata")


tlc_monthly_ingestion()
