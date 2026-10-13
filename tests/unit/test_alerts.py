from nyc_mobility.alerts import build_failure_message


def test_failure_message_contains_key_details():
    # Arrange + Act: build a message from known values
    message = build_failure_message(
        dag_id="tlc_monthly_ingestion",
        task_id="ingest_month",
        run_id="manual__x",
        try_number=4,
        error="boom",
    )

    # Assert: everything a person needs to start debugging is in the message
    assert "tlc_monthly_ingestion" in message
    assert "ingest_month" in message
    assert "attempt: 4" in message
    assert "boom" in message
