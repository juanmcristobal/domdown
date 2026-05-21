"""Tests for Reddit author extraction.

Verifies that the Reddit extractor correctly identifies post author, site,
and title from shreddit-post elements, independent of whether comments are loaded.

NOTE: The Reddit extractor is not yet fully implemented in domdown.
These tests document expected behavior based on the TypeScript implementation.
"""

from domdown import Domdown, DomdownOptions
from domdown.utils.dom import parse_html

REDDIT_URL = "https://www.reddit.com/r/test/comments/abc123/test_post/"

NEW_REDDIT_NO_COMMENTS_HTML = """
<html>
<head>
<title>Test Post : test</title>
</head>
<body>
<h1>Test Post Title</h1>
<shreddit-post
  author="original_poster"
  subreddit-prefixed-name="r/test"
  post-title="Test Post Title"
  score="42"
  comment-count="5"
  created-timestamp="2025-01-15T10:00:00Z"
  permalink="/r/test/comments/abc123/test_post/">
  <div slot="text-body"><p>This is the post body content.</p></div>
</shreddit-post>
<span class="author">logged_in_user</span>
<span class="author">some_commenter</span>
</body>
</html>
"""

NEW_REDDIT_WITH_COMMENTS_HTML = """
<html>
<head>
<title>Test Post : test</title>
</head>
<body>
<h1>Test Post Title</h1>
<shreddit-post
  author="original_poster"
  subreddit-prefixed-name="r/test"
  post-title="Test Post Title"
  score="42"
  comment-count="5"
  created-timestamp="2025-01-15T10:00:00Z"
  permalink="/r/test/comments/abc123/test_post/">
  <div slot="text-body"><p>This is the post body content.</p></div>
</shreddit-post>
<shreddit-comment author="commenter_one" depth="0" score="10"
  permalink="/r/test/comments/abc123/test_post/c1/"
  created="2025-01-15T11:00:00Z">
  <div slot="comment"><p>Nice post!</p></div>
</shreddit-comment>
<shreddit-comment author="commenter_two" depth="0" score="5"
  permalink="/r/test/comments/abc123/test_post/c2/"
  created="2025-01-15T12:00:00Z">
  <div slot="comment"><p>I agree.</p></div>
</shreddit-comment>
<span class="author">logged_in_user</span>
</body>
</html>
"""


class TestRedditAuthorExtraction:
    """Tests for Reddit post author extraction.

    The Reddit extractor is not yet fully implemented. These tests verify
    current behavior and are expected to be updated when the extractor is
    implemented.
    """

    def test_comments_page_without_loaded_comments_returns_post_author_title_site(
        self,
    ) -> None:
        """When comments haven't loaded yet, extractor should return post author, site, and title."""
        doc = parse_html(NEW_REDDIT_NO_COMMENTS_HTML)
        domdown = Domdown(doc, DomdownOptions(url=REDDIT_URL))
        result = domdown.parse()

        assert result.author == "original_poster"
        assert result.site == "r/test"
        assert result.title == "Test Post Title"

    def test_comments_page_with_loaded_comments_returns_post_author(self) -> None:
        """When comments are loaded, extractor should return only the post author."""
        doc = parse_html(NEW_REDDIT_WITH_COMMENTS_HTML)
        domdown = Domdown(doc, DomdownOptions(url=REDDIT_URL))
        result = domdown.parse()

        assert result.author == "original_poster"
