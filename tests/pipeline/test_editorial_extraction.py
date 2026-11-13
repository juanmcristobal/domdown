from pathlib import Path

from bs4 import BeautifulSoup

from domdown import DomdownOptions, ExtractionCriteria, HtmlToMarkdownPipeline
from domdown._document import choose_root, parse_html


FIXTURE = Path(__file__).parents[1] / "fixtures" / "editorial_template.html"


def test_generic_extraction_keeps_article_and_removes_site_template() -> None:
    """Keep editorial structure and references while dropping surrounding site modules."""

    html = FIXTURE.read_text(encoding="utf-8")
    result = HtmlToMarkdownPipeline(DomdownOptions()).run(html)

    assert "Cloud Incident Investigation" in result.markdown
    assert "Investigators identified unauthorized access" in result.markdown
    assert "approved change records" in result.markdown
    assert "https://security.example.org/report" in result.markdown
    assert "| Indicator | Observed value | Action |" in result.markdown
    assert "VendorIntegrationRole" in result.markdown
    assert "aws sts get-caller-identity" in result.markdown
    assert "https://images.example.test/cloud-access-flow.png" in result.markdown
    assert "https://images.example.test/credential-validation.png" in result.markdown
    assert "Credential validation performed after access was confirmed" in result.markdown
    assert "Diagram showing the vendor role" in result.markdown

    for template_text in (
        "Products",
        "Get a demo",
        "Contact us",
        "About the author",
        "Author profile",
        "Unrelated story one",
        "What customers say",
        "Stay informed",
        "All rights reserved",
    ):
        assert template_text not in result.markdown
    assert "data:image/" not in result.markdown
    assert "base64," not in result.markdown


def test_dominant_article_title_outside_article_is_preserved_and_discover_replays() -> None:
    """A detached title header should survive generic extraction and JSON replay."""

    html = FIXTURE.read_text(encoding="utf-8")
    options = DomdownOptions()
    discovered = HtmlToMarkdownPipeline(options).run(html)
    criteria = ExtractionCriteria.from_json(discovered.criteria.to_json())
    replayed = HtmlToMarkdownPipeline(options).run(html, criteria=criteria)

    assert discovered.markdown == replayed.markdown
    assert discovered.document == replayed.document
    assert "# Cloud Incident Investigation" in discovered.markdown
    assert "# Indicators and response" in discovered.markdown
    assert "Blog" not in discovered.markdown


def test_multiple_plausible_articles_use_conservative_fallback() -> None:
    """When two substantial articles compete, retain both rather than crop silently."""

    article_html = []
    for label in ("FIRST-ARTICLE", "SECOND-ARTICLE"):
        paragraphs = "".join(
            f"<p>{label} evidence paragraph {index}. "
            + ("Detailed technical context supports a cautious response. " * 8)
            + "</p>"
            for index in range(4)
        )
        article_html.append(f"<article><h1>{label}</h1>{paragraphs}</article>")
    html = f"<html><body><main>{''.join(article_html)}</main></body></html>"
    soup = parse_html(html)
    selected = choose_root(soup)
    result = HtmlToMarkdownPipeline().run(html)

    assert selected.name == "main"
    assert "FIRST-ARTICLE" in result.markdown
    assert "SECOND-ARTICLE" in result.markdown


def test_cleaned_html_has_no_recommendations_or_footer() -> None:
    """Structural cleanup should remove modules from the selected DOM as well as Markdown."""

    result = HtmlToMarkdownPipeline().run(FIXTURE.read_text(encoding="utf-8"))
    cleaned = BeautifulSoup(result.cleaned_html, "lxml")

    assert cleaned.select_one(".site-navigation") is None
    assert cleaned.select_one(".hero-cta") is None
    assert cleaned.select_one(".author-profile") is None
    assert cleaned.select_one(".recommendations") is None
    assert cleaned.select_one(".customer-testimonials") is None
    assert cleaned.select_one(".newsletter-form") is None
    assert cleaned.find("footer") is None
    assert cleaned.select_one("article table") is not None
