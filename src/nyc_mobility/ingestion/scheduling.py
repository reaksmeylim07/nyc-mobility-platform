from datetime import datetime

from nyc_mobility.ingestion.tlc import parse_year_month


def resolve_year_month(override: str | None, interval_start: datetime | None) -> str:
    """Decide which month a run should load.

    1. An explicit override (e.g. from a manual run's parameter) wins.
    2. Otherwise use the start of the run's data interval.
    3. If neither exists, raise ValueError.
    """
    if override is not None:
        parse_year_month(override)
        return override
    
    if interval_start is not None:
        return interval_start.strftime("%Y-%m")

    raise ValueError("No year_month to load: pass the year_month parameter for manual runs.")