from __future__ import annotations

from domdown._document import choose_root, parse_html
from tests.fixtures import ARTICLE_SHELL_HTML


def test_choose_root_prefers_post_body_when_article_body_is_enabled() -> None:
    """Root selection should favor the post body when that mode is enabled."""

    soup = parse_html(
        "<html><body><main><div class='articlebody'><p>article</p></div><div class='post-body'><p>post</p></div></main></body></html>"
    )

    root = choose_root(soup, prefer_article_body=True)

    assert root.get("class") == ["post-body"]


def test_choose_root_can_flip_priority_order() -> None:
    """The root chooser should respect the caller preference order."""

    soup = parse_html(
        "<html><body><main><div class='articlebody'><p>article</p></div><div class='post-body'><p>post</p></div></main></body></html>"
    )

    root = choose_root(soup, prefer_article_body=False)

    assert root.get("class") == ["articlebody"]


def test_choose_root_prefers_inner_content_container_inside_article_shell() -> None:
    """Article shells should resolve to the inner content container, not the whole wrapper."""

    soup = parse_html(ARTICLE_SHELL_HTML)

    root = choose_root(soup, prefer_article_body=True)

    assert root.name == "div"
    assert root.get("class") == ["content", "content--narrow"]
