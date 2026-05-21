import httpx
import pytest

from domdown.fetch import DEFAULT_UA, _detect_charset, fetch_page

HTML = b"<html><head></head><body>hello</body></html>"


class MockResponse:
    def __init__(self, content_type: str, content: bytes = HTML):
        self.status_code = 200
        self.content = content
        self._headers = {"content-type": content_type}

    @property
    def headers(self) -> dict:
        return self._headers


@pytest.fixture(autouse=True)
def clear_proxy_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.delenv(var, raising=False)


class TestDetectCharset:
    def test_trailing_comma_in_charset(self) -> None:
        content_type = "text/html; charset=utf-8,"
        result = _detect_charset(content_type, HTML)
        assert result == "utf-8"

    def test_quoted_charset(self) -> None:
        content_type = 'text/html; charset="utf-8"'
        result = _detect_charset(content_type, HTML)
        assert result == "utf-8"

    def test_single_quoted_charset(self) -> None:
        content_type = "text/html; charset='utf-8'"
        result = _detect_charset(content_type, HTML)
        assert result == "utf-8"


class TestFetchPageCharset:
    def test_handles_trailing_comma_in_charset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        response = MockResponse("text/html; charset=utf-8,")
        monkeypatch.setattr(httpx, "Client", lambda **kwargs: _MockClient(response))
        result = fetch_page("https://example.com", DEFAULT_UA)
        assert "hello" in result

    def test_handles_quoted_charset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        response = MockResponse('text/html; charset="utf-8"')
        monkeypatch.setattr(httpx, "Client", lambda **kwargs: _MockClient(response))
        result = fetch_page("https://example.com", DEFAULT_UA)
        assert "hello" in result


class _MockClient:
    def __init__(self, response: MockResponse) -> None:
        self._response = response

    def __enter__(self) -> "_MockClient":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def get(self, url: str) -> MockResponse:
        return self._response
