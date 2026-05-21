from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html, build_quoted_post
from domdown.utils.dom import escape_html


@dataclass
class ThreadsPost:
    username: str
    date: str
    permalink: str
    content: str
    element: Tag


class ThreadsExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)

        all_pagelets = document.select('[data-pagelet^="threads_post_page_"]')
        self.pagelets = [p for p in all_pagelets if p.select_one('a[href^="/@"], time[datetime]')]

        self.region_container: Optional[Tag] = None
        if not self.pagelets:
            region = document.select_one('div[role="region"]')
            if region and region.select_one('a[href^="/@"]'):
                self.region_container = region

    def can_extract(self) -> bool:
        return len(self.pagelets) > 0 or self.region_container is not None

    def extract(self) -> ExtractorResult:
        if not self.pagelets and self.region_container:
            return self._extract_from_region(self.region_container)

        main_author = self._get_username(self.pagelets[0])

        thread_posts: List[ThreadsPost] = []
        reply_posts: List[List[ThreadsPost]] = []
        thread_ended = False

        for pagelet in self.pagelets:
            posts = self._get_posts_from_pagelet(pagelet)
            if not posts:
                continue

            if not thread_ended and posts[0].username == main_author and len(posts) == 1:
                thread_posts.append(posts[0])
            else:
                thread_ended = True
                reply_posts.append(posts)

        post_content = "\n<hr>\n".join(p.content for p in thread_posts)

        comments = self._extract_comments(reply_posts) if self.options.include_replies is not False else ""

        content_html = build_content_html("threads", post_content, comments)
        author = f"@{main_author}"
        description = self._create_description(thread_posts[0].element if thread_posts else None)
        title = self.post_title(author, "Threads")
        published = thread_posts[0].date if thread_posts else ""

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": title,
                "author": author,
                "site": "Threads",
                "description": description,
                "published": published if published else None,
            },
        )

    def _extract_from_region(self, region: Tag) -> ExtractorResult:
        main_author = self._get_username(region)
        if not main_author:
            return ExtractorResult(content="", content_html="")
        author = f"@{main_author}"

        post_content = self._extract_post_content(region)

        comments = self._extract_comments_from_json(main_author) if self.options.include_replies is not False else ""

        content_html = build_content_html("threads", post_content, comments)
        description = self._create_description(region)
        date = self._get_date(region)

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": self.post_title(author, "Threads"),
                "author": author,
                "site": "Threads",
                "description": description,
                "published": date if date else None,
            },
        )

    def _extract_comments_from_json(self, main_author: str) -> str:
        scripts = self.document.select('script[type="application/json"]')

        all_posts: List[dict] = []
        seen = set()

        for script in scripts:
            raw = script.get_text()
            if (raw.count('"text_fragments"') < 2) or '"username"' not in raw:
                continue

            try:
                data = json.loads(raw)
                for post in self._find_posts_in_json(data, 0):
                    key = f"{post['username']}:{post['text'][:80]}"
                    if key in seen:
                        continue
                    seen.add(key)
                    all_posts.append(post)
            except Exception:
                pass

        if len(all_posts) < 2:
            return ""

        comment_data: List[CommentData] = []
        is_first_by_main_author = True
        for post in all_posts:
            if is_first_by_main_author and post["username"] == main_author:
                is_first_by_main_author = False
                continue
            comment_data.append(
                CommentData(
                    author=f"@{post['username']}",
                    date="",
                    content=f"<p>{escape_html(post['text'])}</p>",
                    depth=0,
                )
            )

        return build_comment_tree(comment_data) if comment_data else ""

    def _find_posts_in_json(self, obj: any, depth: int) -> List[dict]:
        results: List[dict] = []
        if depth > 35 or obj is None or not isinstance(obj, dict):
            return results

        if obj.get("user") and isinstance(obj["user"], dict) and obj["user"].get("username"):
            text = self._extract_text_from_json(obj, 0)
            if text:
                results.append({"username": obj["user"]["username"], "text": text})

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "quoted_post":
                    continue
                results.extend(self._find_posts_in_json(value, depth + 1))

        return results

    def _extract_text_from_json(self, obj: any, depth: int) -> Optional[str]:
        if depth > 10 or obj is None or not isinstance(obj, dict):
            return None

        if (
            obj.get("text_fragments")
            and isinstance(obj["text_fragments"], dict)
            and obj["text_fragments"].get("fragments")
        ):
            fragments = obj["text_fragments"]["fragments"]
            if isinstance(fragments, list):
                return "".join(
                    (
                        f.get("plaintext", "") or f"@{f['mention_fragment']['username']}"
                        if f.get("mention_fragment")
                        else f.get("linkified_web_url", "") or ""
                    )
                    for f in fragments
                    if isinstance(f, dict)
                )

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "quoted_post":
                    continue
                result = self._extract_text_from_json(value, depth + 1)
                if result:
                    return result

        return None

    def _get_posts_from_pagelet(self, pagelet: Tag) -> List[ThreadsPost]:
        containers = pagelet.select("[data-pressable-container]")
        posts: List[ThreadsPost] = []

        for container in containers:
            parent = container.parent
            if parent and parent.select_one("[data-pressable-container]"):
                continue

            username = self._get_username(container)
            if not username:
                continue

            posts.append(
                ThreadsPost(
                    username=username,
                    date=self._get_date(container),
                    permalink=self._get_permalink(container),
                    content=self._extract_post_content(container),
                    element=container,
                )
            )

        return posts

    def _extract_comments(self, reply_posts: List[List[ThreadsPost]]) -> str:
        comment_data: List[CommentData] = []

        for posts in reply_posts:
            for i, post in enumerate(posts):
                depth = 0 if len(posts) == 1 else i
                comment_data.append(
                    CommentData(
                        author=f"@{post.username}",
                        date=post.date,
                        content=post.content,
                        depth=depth,
                        url=post.permalink if post.permalink else None,
                    )
                )

        return build_comment_tree(comment_data) if comment_data else ""

    def _get_username(self, container: Tag) -> str:
        links = container.select('a[href^="/@"][role="link"]')
        for link in links:
            text = link.get_text(strip=True)
            if text and "profile picture" not in text:
                return text

        first_link = container.select_one('a[href^="/@"]')
        if first_link:
            href = first_link.get("href", "")
            match = re.search(r"/@([^/]+)", href)
            return match.group(1) if match else ""

        return ""

    def _get_date(self, container: Tag) -> str:
        time_el = container.select_one("time[datetime]")
        if not time_el:
            return ""
        datetime = time_el.get("datetime", "")
        try:
            from datetime import datetime as dt

            return dt.fromisoformat(datetime.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            return ""

    def _get_permalink(self, container: Tag) -> str:
        time_link = container.select_one('a[href*="/post/"]')
        if not time_link:
            return ""
        href = time_link.get("href", "")
        return href if href.startswith("http") else f"https://www.threads.com{href}"

    def _extract_post_content(self, container: Tag) -> str:
        parts: List[str] = []

        all_spans = container.select('span[dir="auto"]')

        for span in all_spans:
            if span.parent and (span.parent.name == "a" and span.parent.get("href", "").startswith("/@")):
                continue
            if span.parent and span.parent.name == "a" and "/post/" in span.parent.get("href", ""):
                continue
            if span.parent and span.parent.name == "a" and "l.threads.com" in span.parent.get("href", ""):
                continue
            if span.parent and span.parent.name == "time":
                continue
            if span.parent and span.parent.get("role") == "button":
                continue

            text = span.get_text(strip=True)
            if not text or text in ("Author", "·", "Top", "View activity"):
                continue
            if re.match(r"^\d{2}/\d{2}/\d{2}$", text):
                continue
            if re.match(r"^@?\w+/post/\w+$", text):
                continue

            cleaned = self._strip_thread_number(text)
            if not cleaned:
                continue

            cleaned_html = self._clean_text(span)
            if cleaned_html:
                parts.append(f"<p>{cleaned_html}</p>")

        images = self._extract_images(container)
        if images:
            parts.append(images)

        card = self._extract_link_card(container)
        if card:
            parts.append(card)

        quoted = self._extract_quoted_post(container)
        if quoted:
            parts.append(quoted)

        return "\n".join(parts)

    def _clean_text(self, span: Tag) -> str:
        clone = copy.copy(span)

        self._remove_thread_numbers(clone)

        for link in clone.select("a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)

            if re.search(r"/@[\w.]+/post/", href):
                link.decompose()
                continue

            if href and "l.threads.com" in href:
                link["href"] = self._unwrap_redirect_url(href)
            elif href.startswith("/@"):
                username = href.replace("/@", "")
                link["href"] = f"https://www.threads.com/@{username}"
                link.string = f"@{username}"
            else:
                link["href"] = href if href.startswith("http") else f"https://www.threads.com{href}"

            link.string = text

        for el in clone.select("span, div"):
            el.unwrap()

        html = (clone.decode_contents() or clone.get_text() or "").strip()
        html = re.sub(r"<!--.*?-->", "", html)
        html = re.sub(r"\s+", " ", html).strip()

        return html

    def _strip_thread_number(self, text: str) -> str:
        return re.sub(r"\s*\d+\s*/\s*\d+\s*$", "", text).strip()

    def _remove_thread_numbers(self, container: Tag) -> None:
        divs = container.select("div")
        for div in divs:
            text = div.get_text(strip=True)
            if re.match(r"^\d+/\d+$", text) and len(div.select("span")) >= 2:
                div.decompose()

    def _unwrap_redirect_url(self, href: str) -> str:
        try:
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(href)
            actual = parse_qs(parsed.query).get("u", [None])[0]
            return actual if actual else href
        except Exception:
            return href

    def _extract_images(self, container: Tag) -> str:
        images: List[str] = []

        for img in container.select("img"):
            alt = img.get("alt", "")
            src = img.get("src", "")
            if "profile picture" in alt or not src:
                continue
            parent = img.parent
            if parent and parent.name == "a" and "l.threads.com" in parent.get("href", ""):
                continue
            width = int(img.get("width", "0"))
            if width > 0 and width <= 48:
                continue

            images.append(f'<img src="{escape_html(src)}" alt="{escape_html(alt)}" />')

        return "\n".join(images)

    def _extract_link_card(self, container: Tag) -> str:
        card_links = container.select('a[href*="l.threads.com"]')
        for card_link in card_links:
            img = card_link.select_one("img")
            if not img:
                continue

            href = card_link.get("href", "")
            actual_url = self._unwrap_redirect_url(href)
            img_src = img.get("src", "")
            img_alt = img.get("alt", "")

            if img_src:
                return f'<a href="{escape_html(actual_url)}"><img src="{escape_html(img_src)}" alt="{escape_html(img_alt)}" /></a>'
        return ""

    def _extract_quoted_post(self, container: Tag) -> str:
        nested_pressable = container.select_one("[data-pressable-container]")
        if nested_pressable:
            return self._extract_quoted_post_from(nested_pressable)

        post_links = container.select('a[href*="/post/"]')
        for link in post_links:
            text = link.get_text(strip=True)
            if re.match(r"^\d{2}/\d{2}/\d{2}$", text):
                continue

            href = link.get("href", "")
            match = re.search(r"/@([^/]+)/post/", href)
            if not match:
                continue

            username = match.group(1)
            content = f"<p>{escape_html(text)}</p>"
            permalink = href if href.startswith("http") else f"https://www.threads.com{href}"

            return build_quoted_post(
                type("QuotedPostData", (), {"author": f"@{username}", "content": content.strip(), "url": permalink})()
            )

        return ""

    def _extract_quoted_post_from(self, quoted_container: Tag) -> str:
        username = self._get_username(quoted_container)
        date = self._get_date(quoted_container)

        text_spans = quoted_container.select('span[dir="auto"]')
        content = ""
        for span in text_spans:
            if span.parent and span.parent.get("role") == "button":
                continue
            if span.parent and span.parent.name == "time":
                continue
            link = span.parent if span.parent and span.parent.name == "a" else None
            if link and link.get("href", "").startswith("/@") and "/post/" not in link.get("href", ""):
                continue

            text = span.get_text(strip=True)
            if not text or text in ("·", "Author"):
                continue
            if re.match(r"^\d{2}/\d{2}/\d{2}$", text):
                continue
            cleaned = self._strip_thread_number(text)
            if cleaned:
                content += f"<p>{escape_html(cleaned)}</p>\n"

        return build_quoted_post(
            type(
                "QuotedPostData",
                (),
                {
                    "author": f"@{username}" if username else None,
                    "date": date if date else None,
                    "content": content.strip(),
                },
            )()
        )

    def _create_description(self, container: Optional[Tag]) -> str:
        if not container:
            return ""

        spans = container.select('span[dir="auto"]')
        for span in spans:
            if span.parent and span.parent.name == "a" and span.parent.get("href", "").startswith("/@"):
                continue
            if span.parent and span.parent.get("role") == "button":
                continue
            if span.parent and span.parent.name == "a" and "/post/" in span.parent.get("href", ""):
                continue
            if span.parent and span.parent.name == "time":
                continue
            text = span.get_text(strip=True) or ""
            if not text or text in ("Author", "·", "Top", "View activity"):
                continue
            if re.match(r"^\d{2}/\d{2}/\d{2}$", text):
                continue
            cleaned = self._strip_thread_number(text)
            if cleaned:
                return cleaned[:140].replace(r"\s+", " ")

        return ""
