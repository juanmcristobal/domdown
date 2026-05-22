from __future__ import annotations

from bs4 import BeautifulSoup, Tag


def choose_root(soup: BeautifulSoup, prefer_article_body: bool = True) -> Tag:
    selectors = [".post-body", ".articlebody", "article", "main", "body"] if prefer_article_body else [
        ".articlebody",
        ".post-body",
        "article",
        "main",
        "body",
    ]
    for selector in selectors:
        root = soup.select_one(selector)
        if isinstance(root, Tag):
            return root
    return soup.body if isinstance(soup.body, Tag) else soup
