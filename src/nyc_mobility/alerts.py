import requests


def build_failure_message(
    dag_id: str, task_id: str, run_id: str, try_number: int, error: object
) -> str:
    """Format a human-readable failure alert."""
    return f"[FAILED] {dag_id}.{task_id}\nrun: {run_id}\nattempt: {try_number}\nerror: {error}"


def send_alert(message: str, webhook_url: str | None) -> None:
    """Post the alert to a webhook (e.g. Slack). Without a URL, print it to the log."""
    if not webhook_url:
        print(f"[ALERT] {message}")
        return
    response = requests.post(webhook_url, json={"text": message}, timeout=10)
    response.raise_for_status()
