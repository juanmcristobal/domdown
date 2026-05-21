import httpx
import pytest

from domdown.fetch import DEFAULT_UA, _get_proxy_url, fetch_page

HTML = b"<html><head></head><body>hello</body></html>"


class MockResponse:
    def __init__(self, content_type: str = "text/html") -> None:
        self.status_code = 200
        self.content = HTML
        self._headers = {"content-type": content_type}

    @property
    def headers(self) -> dict:
        return self._headers


class _MockClient:
    def __init__(self, response: MockResponse, **kwargs: object) -> None:
        self._response = response
        self._proxy = kwargs.get("proxy")

    def __enter__(self) -> "_MockClient":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def get(self, url: str) -> MockResponse:
        return self._response


@pytest.fixture(autouse=True)
def clear_proxy_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in (
        "HTTPS_PROXY",
        "https_proxy",
        "HTTP_PROXY",
        "http_proxy",
        "ALL_PROXY",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    ):
        monkeypatch.delenv(var, raising=False)


class TestGetProxyUrl:
    def test_no_proxy_vars_returns_none(self) -> None:
        result = _get_proxy_url("https://example.com")
        assert result is None

    def test_https_proxy_used_for_https_urls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        result = _get_proxy_url("https://example.com")
        assert result == "http://proxy.example.com:8080"

    def test_http_proxy_used_for_http_urls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTP_PROXY", "http://proxy.example.com:8080")
        result = _get_proxy_url("http://example.com")
        assert result == "http://proxy.example.com:8080"

    def test_all_proxy_as_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ALL_PROXY", "http://proxy.example.com:8080")
        result = _get_proxy_url("https://example.com")
        assert result == "http://proxy.example.com:8080"

    def test_https_proxy_takes_precedence_over_all_proxy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://specific.example.com:8080")
        monkeypatch.setenv("ALL_PROXY", "http://fallback.example.com:8080")
        result = _get_proxy_url("https://example.com")
        assert result == "http://specific.example.com:8080"

    def test_https_proxy_not_used_for_http_urls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        result = _get_proxy_url("http://example.com")
        assert result is None


class TestNoProxyExclusions:
    def test_wildcard_bypasses_proxy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("NO_PROXY", "*")
        result = _get_proxy_url("https://example.com")
        assert result is None

    def test_exact_hostname_bypasses_proxy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("NO_PROXY", "example.com")
        result = _get_proxy_url("https://example.com")
        assert result is None

    def test_unrelated_hostname_does_not_bypass_proxy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("NO_PROXY", "other.com")
        result = _get_proxy_url("https://example.com")
        assert result == "http://proxy.example.com:8080"

    def test_leading_dot_matches_subdomain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("NO_PROXY", ".example.com")
        result = _get_proxy_url("https://sub.example.com")
        assert result is None

    def test_leading_dot_matches_bare_domain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("NO_PROXY", ".example.com")
        result = _get_proxy_url("https://example.com")
        assert result is None

    def test_leading_dot_does_not_match_unrelated_domain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("NO_PROXY", ".example.com")
        result = _get_proxy_url("https://notexample.com")
        assert result == "http://proxy.example.com:8080"

    def test_comma_separated_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        monkeypatch.setenv("NO_PROXY", "other.com, example.com, another.com")
        result = _get_proxy_url("https://example.com")
        assert result is None

    def test_malformed_proxy_url_returns_raw(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Note: Python fetch doesn't validate proxy URLs - malformed URLs pass through."""
        monkeypatch.setenv("HTTPS_PROXY", "not-a-valid-url")
        result = _get_proxy_url("https://example.com")
        assert result == "not-a-valid-url"


class TestFetchPageProxyIntegration:
    def test_no_proxy_uses_global_fetch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        response = MockResponse()
        monkeypatch.setattr(httpx, "Client", lambda **kwargs: _MockClient(response))
        result = fetch_page("https://example.com", DEFAULT_UA)
        assert "hello" in result

    def test_fetch_page_with_proxy_env_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When HTTPS_PROXY is set, httpx attempts proxy connection which fails."""
        monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example.com:8080")
        with pytest.raises(Exception):
            fetch_page("https://example.com", DEFAULT_UA)

    def test_malformed_proxy_url_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Malformed proxy URL is passed to httpx which fails on connection."""
        monkeypatch.setenv("HTTPS_PROXY", "not-a-valid-url")
        with pytest.raises(Exception):
            fetch_page("https://example.com", DEFAULT_UA)
