from __future__ import annotations

from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html
from domdown.utils.dom import escape_html


class MastodonExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)

        self.main_post = document.select_one(".detailed-status__wrapper")

        wrappers = document.select(".status__wrapper")
        self.reply_statuses = [w for w in wrappers if w.select_one(".status[data-id]")]

    def can_extract(self) -> bool:
        if not self.main_post:
            return False

        if self.document.get("id") == "mastodon":
            return True

        initial_state = self.document.select_one("script#initial-state")
        if initial_state:
            text = initial_state.get_text()
            if "mastodon/mastodon" in text or '"mastodon"' in text:
                return True

        for link in self.document.select('link[rel="stylesheet"]'):
            href = link.get("href", "")
            if "mastodon" in href:
                return True

        return False

    def extract(self) -> ExtractorResult:
        main_full_handle = self._get_full_handle(self.main_post)
        main_handle = main_full_handle.split("@")[0]
        display_name = self._get_display_name(self.main_post)

        thread_items: List[Tag] = []
        reply_items: List[Tag] = []
        thread_ended = False

        for status in self.reply_statuses:
            handle = self._get_full_handle(status).split("@")[0]
            if not thread_ended and handle == main_handle:
                thread_items.append(status)
            else:
                thread_ended = True
                reply_items.append(status)

        main_content = self._extract_post_content(self.main_post)
        thread_parts = [self._extract_post_content(item) for item in thread_items]
        all_parts = [main_content] + thread_parts
        post_content = "\n<hr>\n".join(p for p in all_parts if p)

        comments = self._extract_comments(reply_items) if self.options.include_replies is not False else ""

        content_html = build_content_html("mastodon", post_content, comments)
        author = display_name or f"@{main_full_handle}"
        description = self._get_description()
        published = self._get_published_date()
        site_name = (
            self.document.select_one('meta[property="og:site_name"]').get("content", "")
            if self.document.select_one('meta[property="og:site_name"]')
            else ""
        )

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": self.post_title(author, site_name or "Mastodon"),
                "author": author,
                "site": site_name or "Mastodon",
                "description": description,
                "published": published if published else None,
            },
        )

    def _get_full_handle(self, container: Tag) -> str:
        account = container.select_one(".display-name__account")
        text = account.get_text(strip=True) if account else ""
        return text.replace("^@", "")

    def _get_display_name(self, container: Tag) -> str:
        name = container.select_one(".display-name__html")
        if not name:
            return ""
        clone = name.clone()
        self._replace_emoji_images(clone)
        return clone.get_text(strip=True) or ""

    def _get_reply_date(self, wrapper: Tag) -> str:
        time_el = wrapper.select_one("time[datetime]")
        if not time_el:
            return ""
        datetime = time_el.get("datetime", "")
        try:
            from datetime import datetime as dt

            return dt.fromisoformat(datetime.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            return ""

    def _get_reply_permalink(self, wrapper: Tag) -> str:
        link = wrapper.select_one("a.status__relative-time[href]")
        if not link:
            return ""
        href = link.get("href", "")
        if not href:
            return ""

        try:
            from urllib.parse import urlparse

            base = urlparse(self.url)
            return href if href.startswith("http") else f"{base.scheme}://{base.netloc}{href}"
        except Exception:
            return href

    def _get_published_date(self) -> str:
        meta = self.document.select_one('meta[property="og:published_time"]')
        if meta:
            content = meta.get("content", "")
            if content:
                try:
                    from datetime import datetime as dt

                    return dt.fromisoformat(content.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass

        if self.main_post:
            time_el = self.main_post.select_one("time[datetime]")
            if time_el:
                try:
                    from datetime import datetime as dt

                    return dt.fromisoformat(time_el.get("datetime", "").replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass

        return ""

    def _get_description(self) -> str:
        if not self.main_post:
            return ""
        text_el = self.main_post.select_one(".status__content__text")
        if not text_el:
            return ""
        return (text_el.get_text() or "").strip()[:140].replace(r"\s+", " ")

    def _extract_post_content(self, container: Tag) -> str:
        parts: List[str] = []

        text = self._extract_text_content(container.select_one(".status__content"))
        if text:
            parts.append(text)

        images = self._extract_images(container)
        if images:
            parts.append(images)

        card = self._extract_link_card(container)
        if card:
            parts.append(card)

        return "\n".join(parts)

    def _extract_text_content(self, content_el: Optional[Tag]) -> str:
        if not content_el:
            return ""

        text_el = content_el.select_one(".status__content__text")
        if not text_el:
            return ""

        clone = text_el.clone()

        self._replace_emoji_images(clone)

        for el in clone.select("span.invisible"):
            el.decompose()

        for el in clone.select("span"):
            el.unwrap()

        return (clone.decode_contents() or clone.get_text() or "").strip()

    def _replace_emoji_images(self, container: Tag) -> None:
        for img in container.select("img.emojione"):
            alt = img.get("alt", "")
            if alt:
                img.replace_with(img.get_text() or alt)
            else:
                img.decompose()

    def _extract_images(self, container: Tag) -> str:
        gallery = container.select_one(".media-gallery")
        if not gallery:
            return ""

        images: List[str] = []
        for link in gallery.select(".media-gallery__item-thumbnail"):
            href = link.get("href", "")
            img = link.select_one("img")
            alt = img.get("alt", "") if img else ""

            if href:
                images.append(f'<img src="{escape_html(href)}" alt="{escape_html(alt)}" />')

        return "\n".join(images)

    def _extract_link_card(self, container: Tag) -> str:
        card = container.select_one("a.status-card[href]")
        if not card:
            return ""

        href = card.get("href", "")
        title = (
            card.select_one(".status-card__title").get_text(strip=True)
            if card.select_one(".status-card__title")
            else ""
        )
        description = (
            card.select_one(".status-card__description").get_text(strip=True)
            if card.select_one(".status-card__description")
            else ""
        )
        img = card.select_one(".status-card__image-image")

        if not title and not href:
            return ""

        html = ""
        if img:
            src = img.get("src", "")
            if src:
                html += (
                    f'<a href="{escape_html(href)}"><img src="{escape_html(src)}" alt="{escape_html(title)}" /></a>\n'
                )
        html += f'<p><a href="{escape_html(href)}">{escape_html(title or href)}</a></p>'
        if description:
            html += f"\n<p>{escape_html(description)}</p>"

        return html

    def _extract_comments(self, reply_items: List[Tag]) -> str:
        if not reply_items:
            return ""

        current_depth = 0
        comment_data: List[CommentData] = []

        for index, wrapper in enumerate(reply_items):
            handle = self._get_full_handle(wrapper)
            display_name = self._get_display_name(wrapper)
            content = self._extract_post_content(wrapper)
            date = self._get_reply_date(wrapper)
            permalink = self._get_reply_permalink(wrapper)

            status_el = wrapper.select_one(".status--first-in-thread")
            if status_el or index == 0:
                current_depth = 0
            else:
                current_depth += 1

            author = f"{display_name} @{handle}" if display_name else f"@{handle}"
            comment_data.append(
                CommentData(
                    author=author,
                    date=date,
                    content=content,
                    depth=current_depth,
                    url=permalink if permalink else None,
                )
            )

        return build_comment_tree(comment_data)
