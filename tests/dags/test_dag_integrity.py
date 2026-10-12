"""Load every DAG file with real Airflow and check required settings.

Runs inside the Airflow image (make test-dags). Skipped in the normal
unit-test run, where Airflow isn't installed.
"""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("airflow")

from airflow.sdk import DAG  # noqa: E402  (must come after importorskip)

DAGS_DIR = Path(__file__).resolve().parents[2] / "orchestration" / "airflow" / "dags"
DAG_FILES = sorted(DAGS_DIR.glob("*.py"))


def load_dags(path: Path) -> list[DAG]:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # fails the test if the file can't be imported
    return [obj for obj in vars(module).values() if isinstance(obj, DAG)]


def test_dag_folder_is_not_empty():
    assert DAG_FILES, f"No DAG files found in {DAGS_DIR}"


@pytest.mark.parametrize("path", DAG_FILES, ids=lambda p: p.name)
def test_dag_file_defines_at_least_one_dag(path):
    assert load_dags(path), f"{path.name} defines no DAG"


@pytest.mark.parametrize("path", DAG_FILES, ids=lambda p: p.name)
def test_every_dag_has_retries_and_tags(path):
    for dag in load_dags(path):
        assert dag.default_args.get("retries", 0) >= 1, f"{dag.dag_id}: set retries >= 1"
        assert dag.tags, f"{dag.dag_id}: add at least one tag"


def test_tlc_dag_does_not_catch_up():
    dags = {d.dag_id: d for p in DAG_FILES for d in load_dags(p)}
    assert dags["tlc_monthly_ingestion"].catchup is False
