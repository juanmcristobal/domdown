from domdown.domdown import Domdown
from domdown.utils.dom import parse_html


class TestMediaRemoval:
    def test_preserves_video_with_source_children(self) -> None:
        html = """<!DOCTYPE html>
<html>
<head><title>Video With Source</title></head>
<body>
<article>
<h1>Video With Source</h1>
<p>This article includes a real video element that uses nested source tags instead of a src attribute on the video element itself.</p>
<video controls poster="https://example.com/poster.jpg">
	<source src="https://example.com/video.mp4" type="video/mp4">
</video>
<p>The video should remain in the extracted HTML because it has a valid media source.</p>
</article>
</body>
</html>"""

        from domdown.types import DomdownOptions

        doc = parse_html(html)
        result = Domdown(doc, DomdownOptions(url="https://example.com/video-with-source")).parse()

        assert "<video" in result.content
        assert "<source" in result.content
        assert "https://example.com/video.mp4" in result.content
