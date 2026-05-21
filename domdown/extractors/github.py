from __future__ import annotations

import re
from typing import List, Optional

from bs4 import Tag

from domdown.extractors._base import BaseExtractor, ExtractorOptions
from domdown.types import ExtractorResult
from domdown.utils.comments import CommentData, build_comment_tree, build_content_html
from domdown.utils.dom import parse_html, serialize_html


class GitHubExtractor(BaseExtractor):
    def __init__(
        self,
        document: Tag,
        url: str,
        schema_org_data: any = None,
        options: Optional[ExtractorOptions] = None,
    ):
        super().__init__(document, url, schema_org_data, options)
        self.is_issue = bool(re.search(r"/issues/\d+", url))
        self.is_pr = bool(re.search(r"/pull/\d+", url))

    def can_extract(self) -> bool:
        github_indicators = [
            'meta[name="expected-hostname"][content="github.com"]',
            'meta[name="octolytics-url"]',
            'meta[name="github-keyboard-shortcuts"]',
            ".js-header-wrapper",
            "#js-repo-pjax-container",
        ]

        if not any(self.document.select(selector) for selector in github_indicators):
            return False

        if self.is_issue:
            return any(
                self.document.select(selector)
                for selector in [
                    '[data-testid="issue-metadata-sticky"]',
                    '[data-testid="issue-title"]',
                ]
            )

        if self.is_pr:
            return any(
                self.document.select(selector)
                for selector in [
                    ".pull-discussion-timeline",
                    ".discussion-timeline",
                    ".gh-header-title",
                    ".js-issue-title",
                ]
            )

        return False

    def extract(self) -> ExtractorResult:
        repo_info = self._extract_repo_info()

        pr_body = self._get_pr_body() if self.is_pr else None
        if self.is_pr and pr_body:
            content, author, published = self._get_pr_content(pr_body)
        else:
            result = self._get_issue_content()
            content, author, published = result["content"], result["author"], result["published"]

        comments = (
            (self._extract_pr_comments(pr_body) if self.is_pr else self._extract_comments())
            if self.options.include_replies is not False
            else ""
        )
        content_html = build_content_html("github", content, comments)

        return ExtractorResult(
            content=content_html,
            content_html=content_html,
            variables={
                "title": self.document.title or "",
                "author": author,
                "published": published,
                "site": f"GitHub - {repo_info['owner']}/{repo_info['repo']}",
                "description": self._create_description(content_html),
            },
        )

    def _extract_issue_content(self) -> dict:
        issue_container = self.document.select_one('[data-testid="issue-viewer-issue-container"]')
        if not issue_container:
            return {"content": "", "author": "", "published": ""}

        author = self._extract_author(
            issue_container,
            [
                'a[data-testid="issue-body-header-author"]',
                ".IssueBodyHeaderAuthor-module__authorLoginLink--_S7aT",
                ".ActivityHeader-module__AuthorLink--iofTU",
                'a[href*="/users/"][data-hovercard-url*="/users/"]',
                'a[aria-label*="profile"]',
            ],
        )

        issue_time_element = issue_container.select_one("relative-time")
        published = issue_time_element.get("datetime", "") if issue_time_element else ""

        issue_body_element = issue_container.select_one('[data-testid="issue-body-viewer"] .markdown-body')
        if not issue_body_element:
            return {"content": "", "author": author, "published": published}

        content = self._clean_body_content(issue_body_element)

        return {"content": content, "author": author, "published": published}

    def _extract_comments(self) -> str:
        comment_elements = self.document.select("[data-wrapper-timeline-id]")
        processed_comments = set()
        comment_data: List[CommentData] = []

        for comment_element in comment_elements:
            comment_container = comment_element.select_one(".react-issue-comment")
            if not comment_container:
                continue

            comment_id = comment_element.get("data-wrapper-timeline-id")
            if not comment_id or comment_id in processed_comments:
                continue
            processed_comments.add(comment_id)

            author = self._extract_author(
                comment_container,
                [
                    ".ActivityHeader-module__AuthorLink--iofTU",
                    'a[data-testid="avatar-link"]',
                    'a[href^="/"][data-hovercard-url*="/users/"]',
                ],
            )

            time_element = comment_container.select_one("relative-time")
            timestamp = time_element.get("datetime", "") if time_element else ""
            date = ""
            if timestamp:
                try:
                    from datetime import datetime as dt

                    date = dt.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass

            body_element = comment_container.select_one(".markdown-body")
            if not body_element:
                continue

            body_content = self._clean_body_content(body_element)
            if not body_content:
                continue

            comment_data.append(
                CommentData(
                    author=author,
                    date=date,
                    content=body_content,
                )
            )

        return build_comment_tree(comment_data)

    def _get_pr_body(self) -> Optional[Tag]:
        pr_body = self.document.select_one('[id^="pullrequest-"]')
        if pr_body:
            return pr_body
        return self.document.select_one(".timeline-comment")

    def _get_pr_content(self, pr_body: Optional[Tag]) -> dict:
        body_el = (pr_body.select_one(".comment-body.markdown-body") if pr_body else None) or self.document.select_one(
            ".comment-body.markdown-body"
        )
        content = self._clean_body_content(body_el) if body_el else ""

        author_el = (pr_body.select_one(".author") if pr_body else None) or self.document.select_one(
            ".gh-header-meta .author"
        )
        author = author_el.get_text(strip=True) if author_el else ""

        time_el = pr_body.select_one("relative-time") if pr_body else None
        published = time_el.get("datetime", "") if time_el else ""

        return {"content": content, "author": author, "published": published}

    def _extract_pr_comments(self, pr_body: Optional[Tag]) -> str:
        all_comments = self.document.select(".timeline-comment, .review-comment")
        comment_data: List[CommentData] = []

        for comment in all_comments:
            if pr_body and (comment is pr_body or comment.find_parent()):
                continue

            author_el = comment.select_one(".author")
            author = author_el.get_text(strip=True) if author_el else ""

            time_element = comment.select_one("relative-time")
            timestamp = time_element.get("datetime", "") if time_element else ""
            date = ""
            if timestamp:
                try:
                    from datetime import datetime as dt

                    date = dt.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    pass

            body_el = comment.select_one(".comment-body.markdown-body")
            if not body_el:
                continue

            body_content = self._clean_body_content(body_el)
            if not body_content:
                continue

            comment_data.append(
                CommentData(
                    author=author,
                    date=date,
                    content=body_content,
                )
            )

        return build_comment_tree(comment_data)

    def _extract_author(self, container: Tag, selectors: List[str]) -> str:
        for selector in selectors:
            author_link = container.select_one(selector)
            if author_link:
                href = author_link.get("href", "")
                if href:
                    if href.startswith("/"):
                        return href[1:]
                    if "github.com/" in href:
                        match = re.search(r"github\.com\/([^\/\?#]+)", href)
                        if match and match.group(1):
                            return match.group(1)
        return "Unknown"

    def _clean_body_content(self, body_element: Tag) -> str:
        clean_body = body_element.clone()

        for el in clean_body.select("button, [data-testid*='button'], [data-testid*='menu']"):
            el.decompose()

        for el in clean_body.select(".js-clipboard-copy, .zeroclipboard-container"):
            el.decompose()

        for pre in clean_body.select('div.highlight[class*="highlight-source-"] pre, div.highlight pre'):
            wrapper = pre.parent
            if not wrapper:
                continue

            lang_match = re.search(r"highlight-source-(\w+)", wrapper.get("class", ""))
            lang = lang_match.group(1) if lang_match else ""

            content = wrapper.get("data-snippet-clipboard-copy-content") or pre.get_text()

            code = Tag(name="code")
            if lang:
                code["class"] = f"language-{lang}"
                code["data-lang"] = lang
            code.string = content

            new_pre = Tag(name="pre")
            new_pre.append(code)
            wrapper.replace_with(new_pre)

        return serialize_html(clean_body).strip()

    def _extract_number(self) -> str:
        url_match = re.search(r"/(issues|pull)/(\d+)", self.url)
        if url_match:
            return url_match.group(2)

        title_element = self.document.select_one("h1")
        title_match = title_element.get_text(strip=True) if title_element else ""
        match = re.search(r"#(\d+)", title_match) if title_match else None
        return match.group(1) if match else ""

    def _extract_repo_info(self) -> dict:
        url_match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", self.url)
        if url_match:
            return {"owner": url_match.group(1), "repo": url_match.group(2)}

        title_match = re.search(r"([^\/\s]+)\/([^\/\s]+)", self.document.title or "")
        return (
            {"owner": title_match.group(1), "repo": title_match.group(2)} if title_match else {"owner": "", "repo": ""}
        )

    def _create_description(self, content: str) -> str:
        if not content:
            return ""

        temp_div = parse_html(content)
        text = temp_div.get_text(strip=True) if temp_div else ""
        return text[:140].replace(r"\s+", " ") if text else ""
