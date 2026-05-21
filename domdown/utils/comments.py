from dataclasses import dataclass
from typing import List, Optional

from domdown.utils.dom import escape_html, is_dangerous_url


@dataclass
class CommentData:
    author: str
    date: str
    content: str
    depth: Optional[int] = None
    score: Optional[str] = None
    url: Optional[str] = None


@dataclass
class QuotedPostData:
    content: str
    author: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None


def _build_comment(comment: CommentData) -> str:
    author_html = f'<span class="comment-author"><strong>{escape_html(comment.author)}</strong></span>'

    safe_url = comment.url if comment.url and not is_dangerous_url(comment.url) else None
    if safe_url:
        date_html = f'<a href="{escape_html(safe_url)}" class="comment-link">{escape_html(comment.date)}</a>'
    else:
        date_html = f'<span class="comment-date">{escape_html(comment.date)}</span>'

    score_html = ""
    if comment.score:
        score_html = f' · <span class="comment-points">{escape_html(comment.score)}</span>'

    return f"""<div class="comment">
	<div class="comment-metadata">
		{author_html} · {date_html}{score_html}
	</div>
	<div class="comment-content">{comment.content}</div>
</div>"""


def build_comment_tree(comments: List[CommentData]) -> str:
    parts: List[str] = []
    blockquote_stack: List[int] = []

    for comment in comments:
        depth = comment.depth if comment.depth is not None else 0

        if depth == 0:
            while blockquote_stack:
                parts.append("</blockquote>")
                blockquote_stack.pop()
            parts.append("<blockquote>")
            blockquote_stack.append(0)
        else:
            current_depth = blockquote_stack[-1] if blockquote_stack else -1
            if depth < current_depth:
                while blockquote_stack and blockquote_stack[-1] >= depth:
                    parts.append("</blockquote>")
                    blockquote_stack.pop()
            new_current_depth = blockquote_stack[-1] if blockquote_stack else -1
            if depth > new_current_depth:
                parts.append("<blockquote>")
                blockquote_stack.append(depth)

        parts.append(_build_comment(comment))

    while blockquote_stack:
        parts.append("</blockquote>")
        blockquote_stack.pop()

    return "".join(parts)


def build_comment(comment: CommentData) -> str:
    return _build_comment(comment)


def build_content_html(site: str, post_content: str, comments: str) -> str:
    comments_section = ""
    if comments:
        comments_section = f"""
				<hr>
				<div class="{site} comments">
					<h2>Comments</h2>
					{comments}
				</div>
			"""
    return f"""<article data-domdown>
			<div class="{site} post">
				<div class="post-content">
					{post_content}
				</div>
			</div>
			{comments_section}
		</article>"""


def build_quoted_post(post: QuotedPostData) -> str:
    header = ""
    if post.author:
        header = f"<p><strong>{escape_html(post.author)}</strong>"
        if post.date:
            header += f" · {escape_html(post.date)}"
        header += "</p>"

    footer = ""
    if post.url:
        safe_url = "" if is_dangerous_url(post.url) else post.url
        if safe_url:
            footer = f'\n<p><a href="{escape_html(safe_url)}">{escape_html(safe_url)}</a></p>'

    return f'<blockquote class="quoted-post">{header}{post.content}{footer}</blockquote>'
