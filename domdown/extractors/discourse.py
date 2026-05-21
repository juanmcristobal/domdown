from __future__ import annotations

from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html
from domdown.utils.dom import serialize_html


class DiscourseExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        generator = document.select_one('meta[name="generator"]')
        self.is_discourse = (generator.get("content", "") or "").startswith("Discourse") if generator else False

    def can_extract(self) -> bool:
        return self.is_discourse and bool(self.document.select_one(".topic-post"))

    def extract(self) -> ExtractorResult:
        title = self._get_topic_title()
        site_name = (
            self.document.select_one('meta[property="og:site_name"]').get("content", "")
            if self.document.select_one('meta[property="og:site_name"]')
            else ""
        )
        published = self._get_published_date()

        posts = self.document.select(".topic-post")
        op = None
        for p in posts:
            if "topic-owner" in p.get("class", []):
                op = p
                break

        post_content = self._extract_post_content(op) if op else ""
        op_author = self._get_author(op) if op else ""

        reply_posts = [p for p in posts if p is not op]
        comments = self._extract_comments(reply_posts) if self.options.include_replies is not False else ""

        content_html = build_content_html("discourse", post_content, comments)
        author = op_author or self._get_author(posts[0]) if posts else ""
        description = self._get_post_text(op)[:140].replace(r"\s+", " ") if op else ""

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": title,
                "author": author,
                "site": site_name or "Discourse",
                "description": description,
                "published": published if published else None,
            },
        )

    def _get_topic_title(self) -> str:
        fancy = self.document.select_one(".fancy-title")
        if fancy:
            return fancy.get_text(strip=True)

        h1 = self.document.select_one("h1[data-topic-id]")
        if h1:
            clone = h1.clone()
            for el in clone.select("svg, .topic-statuses"):
                el.decompose()
            return clone.get_text(strip=True)

        return ""

    def _get_tags(self) -> List[str]:
        return [
            el.get("data-tag-name") or el.get_text(strip=True)
            for el in self.document.select("a.discourse-tag")
            if (el.get("data-tag-name") or el.get_text(strip=True))
        ]

    def _get_published_date(self) -> str:
        meta = self.document.select_one('meta[property="article:published_time"]')
        if meta:
            content = meta.get("content", "")
            if content:
                try:
                    from datetime import datetime as dt

                    return dt.fromisoformat(content.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass
        return ""

    def _get_author(self, post: Optional[Tag]) -> str:
        if not post:
            return ""
        name_link = post.select_one(".names a[data-user-card]")
        if name_link:
            return name_link.get("data-user-card") or name_link.get_text(strip=True)
        return ""

    def _get_post_date(self, post: Tag) -> str:
        date_el = post.select_one(".relative-date[data-time]")
        if not date_el:
            return ""
        time_val = int(date_el.get("data-time", "0"))
        if not time_val:
            return ""
        try:
            from datetime import datetime as dt

            return dt.fromtimestamp(time_val / 1000).strftime("%Y-%m-%d")
        except Exception:
            return ""

    def _get_post_permalink(self, post: Tag) -> str:
        link = post.select_one("a.post-date[href]")
        if not link:
            return ""
        href = link.get("href", "")
        if not href:
            return ""

        try:
            from urllib.parse import urlparse

            base = urlparse(self.url)
            return f"{base.scheme}://{base.netloc}{href}"
        except Exception:
            return href

    def _get_like_count(self, post: Tag) -> str:
        btn = post.select_one("button.like-count")
        count = btn.get_text(strip=True) if btn else ""
        return f"{count} likes" if count else ""

    def _get_post_text(self, post: Optional[Tag]) -> str:
        if not post:
            return ""
        cooked = post.select_one(".cooked")
        if not cooked:
            return ""
        return cooked.get_text(strip=True) or ""

    def _extract_post_content(self, post: Tag) -> str:
        cooked = post.select_one(".cooked")
        if not cooked:
            return ""

        clone = cooked.clone()

        for el in clone.select(".cooked-selection-barrier"):
            el.decompose()

        for a in clone.select("a.anchor"):
            a.decompose()

        return serialize_html(clone)

    def _extract_comments(self, reply_posts: List[Tag]) -> str:
        if not reply_posts:
            return ""

        comment_data: List[CommentData] = []
        for post in reply_posts:
            author = self._get_author(post)
            content = self._extract_post_content(post)
            date = self._get_post_date(post)
            url = self._get_post_permalink(post)
            likes = self._get_like_count(post)

            comment_data.append(
                CommentData(
                    author=author,
                    date=date,
                    content=content,
                    depth=0,
                    score=likes if likes else None,
                    url=url if url else None,
                )
            )

        return build_comment_tree(comment_data)
