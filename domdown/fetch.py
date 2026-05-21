from __future__ import annotations

import os
import re
from typing import Optional
from urllib.parse import urlparse

import httpx

MAX_SIZE = 5 * 1024 * 1024  # 5MB
FETCH_TIMEOUT = 10.0  # seconds

DEFAULT_UA = "Mozilla/5.0 (compatible; Domdown/1.0; +https://domdown.md)"
BOT_UA = DEFAULT_UA + " bot"

BOT_UA_DOMAINS = ["github.com"]


def get_initial_ua(target_url: str) -> str:
    try:
        hostname = urlparse(target_url).hostname or ""
        if any(hostname == d or hostname.endswith("." + d) for d in BOT_UA_DOMAINS):
            return BOT_UA
    except Exception:
        pass
    return DEFAULT_UA


def _get_proxy_url(target_url: str) -> Optional[str]:
    is_https = target_url.startswith("https:")
    raw = (
        (os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") if is_https else None)
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
        or os.environ.get("ALL_PROXY")
        or os.environ.get("all_proxy")
    )
    if not raw:
        return None

    no_proxy = os.environ.get("NO_PROXY") or os.environ.get("no_proxy") or ""
    if no_proxy:
        hostname = urlparse(target_url).hostname or ""
        for pattern in no_proxy.split(","):
            pattern = pattern.strip()
            if pattern == "*":
                return None
            if pattern.startswith("."):
                if hostname.endswith(pattern) or hostname == pattern[1:]:
                    return None
            elif hostname == pattern or hostname.endswith("." + pattern):
                return None

    return raw


def _validate_content_type(content_type: str) -> None:
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        raise ValueError(f"Not an HTML page (content-type: {content_type})")


def _validate_size(content_length: Optional[int], actual_size: int) -> None:
    if content_length is not None and content_length > MAX_SIZE:
        raise ValueError(f"Page too large ({round(content_length / 1024 / 1024)}MB, max 5MB)")
    if actual_size > MAX_SIZE:
        raise ValueError(f"Page too large ({round(actual_size / 1024 / 1024)}MB, max 5MB)")


def _detect_charset(content_type: str, content: bytes) -> str:
    header_match = re.search(r'charset=["\']?([^\s;,"\']+)', content_type, re.IGNORECASE)
    if header_match:
        return header_match.group(1).lower()

    head = content[:1024].decode("latin-1", errors="replace")
    meta_charset = re.search(r'<meta[^>]+charset=["\']?([^\s"\';>]+)', head, re.IGNORECASE)
    if meta_charset:
        return meta_charset.group(1).lower()

    meta_http_equiv = re.search(r'<meta[^>]+content=["\'][^"\']*charset=([^\s"\';]+)', head, re.IGNORECASE)
    if meta_http_equiv:
        return meta_http_equiv.group(1).lower()

    sniff = content[:8192]
    i = 0
    while i < len(sniff):
        b = sniff[i]
        if 0x80 <= b <= 0x9F:
            return "windows-1252"
        if 0xC0 <= b <= 0xF7:
            seq_len = 2 if b < 0xE0 else (3 if b < 0xF0 else 4)
            valid = True
            for j in range(1, seq_len):
                if i + j >= len(sniff) or (sniff[i + j] & 0xC0) != 0x80:
                    valid = False
                    break
            if valid:
                i += seq_len
                continue
            return "windows-1252"
        i += 1

    return "utf-8"


def _decode_html(content: bytes, content_type: str) -> str:
    charset = _detect_charset(content_type, content)
    if charset in ("windows-1252", "iso-8859-1", "latin1"):
        return content.decode("windows-1252", errors="replace")
    try:
        return content.decode(charset, errors="replace")
    except (LookupError, UnicodeDecodeError):
        return content.decode("utf-8", errors="replace")


def _build_client_kwargs(headers: dict, proxy_url: Optional[str]) -> dict:
    kwargs: dict = {
        "timeout": FETCH_TIMEOUT,
        "follow_redirects": True,
        "max_redirects": 10,
        "headers": headers,
    }
    if proxy_url:
        kwargs["proxy"] = proxy_url
    return kwargs


def fetch_page(
    target_url: str,
    user_agent: Optional[str] = None,
    language: Optional[str] = None,
) -> str:
    ua = user_agent or get_initial_ua(target_url)
    headers: dict = {"User-Agent": ua, "Accept": "text/html,application/xhtml+xml"}
    if language:
        headers["Accept-Language"] = language

    proxy_url = _get_proxy_url(target_url)

    with httpx.Client(**_build_client_kwargs(headers, proxy_url)) as client:
        response = client.get(target_url)

        if response.status_code < 200 or response.status_code >= 300:
            raise ValueError(f"Failed to fetch: {response.status_code}")

        content_type = response.headers.get("content-type", "")
        _validate_content_type(content_type)

        content_length_str = response.headers.get("content-length")
        content_length = int(content_length_str) if content_length_str else None
        _validate_size(content_length, len(response.content))

        return _decode_html(response.content, content_type)


async def fetch_page_async(
    target_url: str,
    user_agent: Optional[str] = None,
    language: Optional[str] = None,
) -> str:
    ua = user_agent or get_initial_ua(target_url)
    headers: dict = {"User-Agent": ua, "Accept": "text/html,application/xhtml+xml"}
    if language:
        headers["Accept-Language"] = language

    proxy_url = _get_proxy_url(target_url)

    async with httpx.AsyncClient(**_build_client_kwargs(headers, proxy_url)) as client:
        response = await client.get(target_url)

        if response.status_code < 200 or response.status_code >= 300:
            raise ValueError(f"Failed to fetch: {response.status_code}")

        content_type = response.headers.get("content-type", "")
        _validate_content_type(content_type)

        content_length_str = response.headers.get("content-length")
        content_length = int(content_length_str) if content_length_str else None
        _validate_size(content_length, len(response.content))

        return _decode_html(response.content, content_type)


def extract_raw_markdown(html: str) -> Optional[str]:
    body_match = re.search(r"<body[^>]*>([\s\S]*?)</body>", html, re.IGNORECASE)
    if not body_match:
        return None

    text_content = body_match.group(1)
    text_content = re.sub(
        r"<(script|style|noscript)[^>]*>[\s\S]*?</\1>",
        "",
        text_content,
        flags=re.IGNORECASE,
    )
    text_content = re.sub(r"<[^>]+>", "", text_content)
    text_content = text_content.strip()

    if not text_content or not _is_markdown_content(text_content):
        return None

    return text_content


def _is_markdown_content(content: str) -> bool:
    signals = 0
    if re.search(r"^#{1,6}\s+\S", content, re.MULTILINE):
        signals += 1
    if re.search(r"\*\*[^*\n]+\*\*", content, re.MULTILINE):
        signals += 1
    if re.search(r"\[[^\]]+\]\([^)]+\)", content, re.MULTILINE):
        signals += 1
    if re.search(r"^\s*[-*+]\s+\S", content, re.MULTILINE):
        signals += 1
    if re.search(r"^\s*\d+\.\s+\S", content, re.MULTILINE):
        signals += 1
    if re.search(r"^>\s+\S", content, re.MULTILINE):
        signals += 1
    if re.search(r"```", content, re.MULTILINE):
        signals += 1
    return signals >= 2


def clean_markdown_content(content: str) -> str:
    markdown = (
        content.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .strip()
    )

    title_match = re.match(r"^# .+\n+", markdown)
    if title_match:
        markdown = markdown[title_match.end() :]

    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    return markdown.strip()
