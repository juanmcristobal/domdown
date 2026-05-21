from __future__ import annotations

import re
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html, build_quoted_post
from domdown.utils.dom import escape_html, serialize_html


class LinkedInExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.post_article = document.select_one('[role="article"].feed-shared-update-v2')

    def can_extract(self) -> bool:
        return bool(self.post_article)

    def extract(self) -> ExtractorResult:
        post_content = self._get_post_content()
        comments = self._extract_comments() if self.options.include_replies is not False else ""
        content_html = build_content_html("linkedin", post_content, comments)

        author = self._get_author_name()
        description = self._create_description()

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": self.post_title(author, "LinkedIn"),
                "author": author,
                "site": "LinkedIn",
                "description": description,
            },
        )

    def _get_post_content(self) -> str:
        if not self.post_article:
            return ""

        quoted_wrapper = self.post_article.select_one(".feed-shared-update-v2__update-content-wrapper")
        text_el = self.post_article.select_one(".update-components-text.update-components-update-v2__commentary")
        text = ""
        if text_el and quoted_wrapper:
            if not quoted_wrapper.contains(text_el):
                text = self._clean_text_content(text_el)
        elif text_el and not quoted_wrapper:
            text = self._clean_text_content(text_el)

        images = self._extract_images()
        video = self._extract_video()
        quoted_post = self._extract_quoted_post(quoted_wrapper)

        html = ""
        if text:
            html += text
        if images:
            html += f"\n{images}"
        if video:
            html += f"\n{video}"
        if quoted_post:
            html += f"\n{quoted_post}"

        return html

    def _get_visible_text(self, el: Tag, also_remove: Optional[str] = None) -> str:
        clone = el.clone()
        selector = f".visually-hidden, {also_remove}" if also_remove else ".visually-hidden"
        for e in clone.select(selector):
            e.decompose()
        return clone.get_text(strip=True) or ""

    def _clean_text_content(self, el: Tag) -> str:
        clone = el.clone()

        for e in clone.select(".visually-hidden, .feed-shared-inline-show-more-text__see-more-less-toggle"):
            e.decompose()

        for link in clone.select("a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if href and text:
                link["href"] = href
                link.string = text
            else:
                link.string = link.get_text()

        for e in clone.select("span, div"):
            e.unwrap()

        html = serialize_html(clone).strip()

        import re

        html = re.sub(r"<!--.*?-->", "", html)

        paragraphs = [
            p.replace("<br>", " ").replace(r"\s+", " ").strip() for p in re.split(r"(?:<br\s*\/?>\s*){2,}|\n{2,}", html)
        ]
        paragraphs = [p for p in paragraphs if p]

        return "\n".join(f"<p>{p}</p>" for p in paragraphs)

    def _extract_quoted_post(self, wrapper: Optional[Tag]) -> str:
        if not wrapper:
            return ""

        actor_title = wrapper.select_one(".update-components-actor__title")
        author_name = (
            self._get_visible_text(
                actor_title, ".update-components-actor__supplementary-actor-info, .text-view-model__verified-icon"
            )
            if actor_title
            else ""
        )

        sub_desc = wrapper.select_one(".update-components-actor__sub-description")
        date = ""
        if sub_desc:
            visible = sub_desc.select_one('[aria-hidden="true"]')
            raw = (visible or sub_desc).get_text(strip=True) if visible or sub_desc else ""
            match = re.match(r"^(\d+\w+)", raw) if raw else None
            date = match.group(1) if match else ""

        text_el = wrapper.select_one(".update-components-text.update-components-update-v2__commentary")
        content = self._clean_text_content(text_el) if text_el else ""

        link_el = wrapper.select_one("a.update-components-mini-update-v2__link-to-details-page")
        post_url = link_el.get("href", "") if link_el else ""
        url = post_url.split("?")[0] if post_url else ""
        if url and not url.startswith("http"):
            url = f"https://www.linkedin.com{url}"

        return build_quoted_post(
            type(
                "QuotedPostData",
                (),
                {
                    "author": author_name if author_name else None,
                    "date": date if date else None,
                    "content": content,
                    "url": url if url else None,
                },
            )()
        )

    def _extract_images(self) -> str:
        if not self.post_article:
            return ""

        images: List[str] = []
        for img in self.post_article.select(".update-components-image img, .feed-shared-image img"):
            src = img.get("src", "")
            alt = img.get("alt", "")
            if src and "profile-displayphoto" not in src and "avm-avatar" not in src:
                images.append(f'<img src="{escape_html(src)}" alt="{escape_html(alt)}" />')

        return "\n".join(images)

    def _extract_video(self) -> str:
        if not self.post_article:
            return ""

        video = self.post_article.select_one(".update-components-linkedin-video video[poster]")
        if not video:
            return ""

        poster = video.get("poster", "")
        return f'<img src="{escape_html(poster)}" alt="Video thumbnail" />'

    def _extract_comments(self) -> str:
        if not self.post_article:
            return ""

        comment_data: List[CommentData] = []

        top_level_comments = self.post_article.select(
            "article.comments-comment-entity:not(.comments-comment-entity--reply)"
        )

        for comment in top_level_comments:
            data = self._extract_comment_data(comment, 0)
            if data:
                comment_data.append(data)

            replies = comment.select(".comments-replies-list article.comments-comment-entity--reply")
            for reply in replies:
                reply_data = self._extract_comment_data(reply, 1)
                if reply_data:
                    comment_data.append(reply_data)

        return build_comment_tree(comment_data) if comment_data else ""

    def _extract_comment_data(self, comment: Tag, depth: int) -> Optional[CommentData]:
        author_elem = comment.select_one(".comments-comment-meta__description-title")
        author = author_elem.get_text(strip=True) if author_elem else ""
        if not author:
            return None

        text_el = comment.select_one(".comments-comment-entity__content .update-components-text")
        content = self._clean_text_content(text_el) if text_el else ""

        time_el = comment.select_one("time.comments-comment-meta__data")
        date = time_el.get_text(strip=True) if time_el else ""

        profile_link = comment.select_one("a.comments-comment-meta__description-container")
        profile_href = profile_link.get("href", "").split("?")[0] if profile_link else ""
        url = (
            f"https://www.linkedin.com{profile_href}"
            if profile_href and not profile_href.startswith("http")
            else profile_href
        )

        reactions_el = comment.select_one(".comments-comment-social-bar__reactions-count--cr span.v-align-middle")
        reactions = reactions_el.get_text(strip=True) if reactions_el else ""

        return CommentData(
            author=author,
            date=date,
            content=content,
            depth=depth,
            score=f"{reactions} reactions" if reactions else None,
            url=url if url else None,
        )

    def _get_author_name(self) -> str:
        if not self.post_article:
            return ""
        name_el = self.post_article.select_one(".update-components-actor__title")
        if not name_el:
            return ""
        return self._get_visible_text(
            name_el, ".text-view-model__verified-icon, .update-components-actor__supplementary-actor-info"
        )

    def _create_description(self) -> str:
        if not self.post_article:
            return ""

        quoted_wrapper = self.post_article.select_one(".feed-shared-update-v2__update-content-wrapper")
        text_el = self.post_article.select_one(".update-components-text.update-components-update-v2__commentary")
        if not text_el or (quoted_wrapper and quoted_wrapper.contains(text_el)):
            return ""

        return self._get_visible_text(text_el)[:140].replace(r"\s+", " ")
