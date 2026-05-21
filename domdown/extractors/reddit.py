from __future__ import annotations

import re
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html
from domdown.utils.dom import parse_html, serialize_html


class RedditExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: any = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.shreddit_post = document.select_one("shreddit-post")
        self.is_old_reddit = bool(document.select_one(".thing.link"))
        if isinstance(options, dict):
            self.options = ExtractorOptions(
                include_replies=options.get("include_replies", "extractors"),
                language=options.get("language"),
                fetch=options.get("fetch"),
            )

    def can_extract(self) -> bool:
        return bool(self.shreddit_post) or self.is_old_reddit

    def can_extract_async(self) -> bool:
        return self._is_comments_page() and not self.is_old_reddit

    def prefers_async(self) -> bool:
        is_browser = False
        return self._is_comments_page() and not self.is_old_reddit and not is_browser

    def _is_comments_page(self) -> bool:
        return bool(re.search(r"/r/.+/comments/", self.url))

    async def extract_async(self) -> ExtractorResult:
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(self.url)
        old_url = urlunparse(("https", "old.reddit.com", parsed.path, parsed.params, parsed.query, parsed.fragment))

        fetch = self.options.fetch if self.options and self.options.fetch else None
        if not fetch:
            raise Exception("Fetch function not available in this environment")

        response = await fetch(old_url, headers={"User-Agent": "Mozilla/5.0 (compatible; Domdown/1.0)"})

        if not response.ok:
            raise Exception(f"Failed to fetch old.reddit.com: {response.status}")

        html = await response.text()
        from bs4 import BeautifulSoup

        doc = BeautifulSoup(html, "lxml")

        return self._extract_old_reddit(doc)

    def extract(self) -> ExtractorResult:
        if self.is_old_reddit:
            return self._extract_old_reddit(self.document)

        post_title = self.document.select_one("h1").get_text(strip=True) if self.document.select_one("h1") else ""
        subreddit = self._get_subreddit()
        post_author = self._get_post_author()
        post_content = self._get_post_content()
        description = self._create_description(post_content)

        comments = self._extract_comments() if self.options.include_replies is not False else ""
        content_html = build_content_html("reddit", post_content, comments)

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": post_title,
                "author": post_author,
                "site": f"r/{subreddit}",
                "description": description,
            },
        )

    def _extract_old_reddit(self, root: Tag) -> ExtractorResult:
        thing_link = root.select_one(".thing.link")
        post_title = (
            thing_link.select_one("a.title").get_text(strip=True)
            if thing_link and thing_link.select_one("a.title")
            else ""
        )
        post_author = thing_link.get("data-author", "") if thing_link else ""
        subreddit = thing_link.get("data-subreddit", "") if thing_link else ""
        post_body_el = thing_link.select_one(".usertext-body .md") if thing_link else None
        post_body = serialize_html(post_body_el) if post_body_el else ""

        comments = ""
        if self.options.include_replies is not False:
            comment_area = root.select_one(".commentarea .sitetable")
            comment_data = self._collect_old_reddit_comments(comment_area) if comment_area else []
            comments = build_comment_tree(comment_data) if comment_data else ""

        content_html = build_content_html("reddit", post_body, comments)
        description = self._create_description(post_body)

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": post_title,
                "author": post_author,
                "site": f"r/{subreddit}",
                "description": description,
            },
        )

    def _get_post_content(self) -> str:
        text_body_el = self.shreddit_post.select_one('[slot="text-body"]') if self.shreddit_post else None
        text_body = serialize_html(text_body_el) if text_body_el else ""
        media_body = (
            self.shreddit_post.select_one("#post-image").outerHTML
            if self.shreddit_post and self.shreddit_post.select_one("#post-image")
            else ""
        )

        return text_body + media_body

    def _extract_comments(self) -> str:
        comments = self.document.select("shreddit-comment")
        return self._process_comments(comments)

    def _get_post_id(self) -> str:
        import re

        match = re.search(r"comments/([a-zA-Z0-9]+)", self.url)
        return match.group(1) if match else ""

    def _get_subreddit(self) -> str:
        import re

        match = re.search(r"/r/([^/]+)", self.url)
        return match.group(1) if match else ""

    def _get_post_author(self) -> str:
        return self.shreddit_post.get("author", "") if self.shreddit_post else ""

    def _create_description(self, post_content: str) -> str:
        if not post_content:
            return ""

        temp_div = parse_html(post_content)
        text = temp_div.get_text(strip=True) if temp_div else ""
        return text[:140].replace(r"\s+", " ") if text else ""

    def _collect_old_reddit_comments(self, container: Optional[Tag], depth: int = 0) -> List[CommentData]:
        result: List[CommentData] = []
        if not container:
            return result

        comments = container.select(":scope > .thing.comment")

        for comment in comments:
            author = comment.get("data-author", "")
            permalink = comment.get("data-permalink", "")
            score_elem = comment.select_one(".entry .tagline .score.unvoted")
            score = score_elem.get_text(strip=True) if score_elem else ""
            time_el = comment.select_one(".entry .tagline time[datetime]")
            datetime = time_el.get("datetime", "") if time_el else ""
            date = ""
            if datetime:
                try:
                    from datetime import datetime as dt

                    date = dt.fromisoformat(datetime.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass
            body_el = comment.select_one(".entry .usertext-body .md")
            body = serialize_html(body_el) if body_el else ""

            result.append(
                CommentData(
                    author=author,
                    date=date,
                    content=body,
                    depth=depth,
                    score=score if score else None,
                    url=f"https://reddit.com{permalink}" if permalink else None,
                )
            )

            child_container = comment.select_one(".child > .sitetable")
            if child_container:
                result.extend(self._collect_old_reddit_comments(child_container, depth + 1))

        return result

    def _process_comments(self, comments: List[Tag]) -> str:
        comment_data: List[CommentData] = []

        for comment in comments:
            depth = int(comment.get("depth", "0"))
            author = comment.get("author", "")
            score = comment.get("score", "0")
            permalink = comment.get("permalink", "")
            comment_el = comment.select_one('[slot="comment"]')
            content = serialize_html(comment_el) if comment_el else ""

            timestamp = comment.get("created", "") or (
                comment.select_one("time").get("datetime", "") if comment.select_one("time") else ""
            )
            date = ""
            if timestamp:
                try:
                    from datetime import datetime as dt

                    date = dt.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass

            comment_data.append(
                CommentData(
                    author=author,
                    date=date,
                    content=content,
                    depth=depth,
                    score=f"{score} points",
                    url=f"https://reddit.com{permalink}" if permalink else None,
                )
            )

        return build_comment_tree(comment_data)
