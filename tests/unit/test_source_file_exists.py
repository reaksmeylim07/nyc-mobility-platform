import pytest
import requests

from nyc_mobility.ingestion import tlc


class FakeResponse:
    """Stands in for a real requests.Response in tests."""

    def __init__(self, status_code: int):
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


@pytest.fixture
def fake_head(monkeypatch):
    """Replace requests.head with a fake that returns the given status code."""

    def install(status_code: int) -> None:
        monkeypatch.setattr(tlc.requests, "head", lambda url, **kwargs: FakeResponse(status_code))

    return install


def test_returns_true_when_file_exists(fake_head):
    fake_head(200)
    assert tlc.source_file_exists("https://example.com/file.parquet") is True


@pytest.mark.parametrize("status_code", [403, 404])
def test_returns_false_when_not_published_yet(fake_head, status_code):
    fake_head(status_code)
    assert tlc.source_file_exists("https://example.com/file.parquet") is False


def test_raises_on_server_error(fake_head):
    fake_head(500)
    with pytest.raises(requests.HTTPError):
        tlc.source_file_exists("https://example.com/file.parquet")
