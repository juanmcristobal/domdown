from domdown._core.selectors import normalize_selector


def test_normalize_selector_translates_deprecated_contains_pseudo() -> None:
    assert normalize_selector('p:contains("related:")') == 'p:-soup-contains("related:")'
    assert normalize_selector("p:CONTAINS ( 'related:' )") == "p:-soup-contains ( 'related:' )"


def test_normalize_selector_does_not_change_quoted_text_or_similar_pseudo_names() -> None:
    selector = 'a[data-label=":contains(text)"]:containsomething("x")'
    assert normalize_selector(selector) == selector
    assert normalize_selector(".article") == ".article"


def test_normalize_selector_preserves_escapes_and_quotes_while_scanning() -> None:
    selector = r'a[title="escaped \":contains(x)"]:contains("needle")'
    assert normalize_selector(selector) == r'a[title="escaped \":contains(x)"]:-soup-contains("needle")'
