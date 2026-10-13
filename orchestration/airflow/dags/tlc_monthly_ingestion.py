"""Monthly ingestion of NYC TLC trip files into the raw zone."""

import os
from datetime import UTC, datetime, timedelta

from airflow.sdk import Param, dag, get_current_context, task
from airflow.sdk.exceptions import AirflowFailException

DATASET = "yellow_tripdata"


def notify_failure(context) -> None:
    """Called by Airflow when a task fails for the final time."""
    from nyc_mobility.alerts import build_failure_message, send_alert

    ti = context["ti"]
    message = build_failure_message(
        ti.dag_id, ti.task_id, ti.run_id, ti.try_number, context.get("exception")
    )
    send_alert(message, os.getenv("ALERT_WEBHOOK_URL"))


@dag(
    dag_id="tlc_monthly_ingestion",
    schedule="@monthly",
    start_date=datetime(2024, 1, 1, tzinfo=UTC),
    catchup=False,
    max_active_runs=2,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": 2.0,
        "max_retry_delay": timedelta(minutes=30),
        "on_failure_callback": notify_failure,
    },
    params={
        "year_month": Param(
            None,
            type=["null", "string"],
            description=(
                "Month to load as YYYY-MM. Required for manual runs; leave empty otherwise."
            ),
        ),
    },
    tags=["ingestion", "tlc"],
)
def tlc_monthly_ingestion():
    @task
    def resolve_month() -> str:
        from nyc_mobility.ingestion.scheduling import resolve_year_month

        context = get_current_context()
        try:
            return resolve_year_month(
                context["params"].get("year_month"),
                context.get("data_interval_start"),
            )
        except ValueError as err:
            raise AirflowFailException(str(err)) from err

    @task.sensor(
        poke_interval=timedelta(hours=6),
        timeout=timedelta(days=60),
        mode="reschedule",
    )
    def wait_for_source_file(dataset: str, year_month: str) -> bool:
        from nyc_mobility.ingestion.tlc import build_source_url, source_file_exists

        return source_file_exists(build_source_url(dataset, year_month))

    @task
    def ingest_month(dataset: str, year_month: str) -> str:
        from dataclasses import replace

        from nyc_mobility.config import Settings
        from nyc_mobility.ingestion.main import run

        settings = replace(Settings.from_env(), tlc_dataset=dataset, tlc_month=year_month)
        run(settings)
        return year_month

    year_month = resolve_month()
    source_ready = wait_for_source_file(DATASET, year_month)
    loaded = ingest_month(DATASET, year_month)
    source_ready >> loaded


tlc_monthly_ingestion_dag = tlc_monthly_ingestion()
