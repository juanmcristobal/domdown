from __future__ import annotations

import soupsieve
from bs4 import BeautifulSoup, Tag

from .._constants import (
    CONTENT_SELECTORS_EXACT,
    CONTENT_SELECTORS_FALLBACK,
    NOISE_MARKERS,
    REFINABLE_CHILD_TAGS,
    ROOT_SELECTORS,
)

_SCORE_HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_SCORE_PRE_CODE_TAGS = frozenset({"pre", "code"})
_SCORE_INTERACTIVE_TAGS = frozenset({"a", "button", "form", "iframe", "input", "select", "textarea"})


def choose_root(soup: BeautifulSoup, prefer_article_body: bool = True) -> Tag:
    """Choose the most relevant content root from a parsed document."""

    selectors = _root_selectors(prefer_article_body)
    candidates = _collect_root_candidates(soup, selectors)
    if candidates:
        candidate = _pick_best_root_candidate(candidates)
        if candidate is not None:
            title_context = _detached_title_context(candidate)
            if title_context is not None:
                return title_context
            return _refine_content_root(candidate)
    if isinstance(soup.body, Tag):
        return _refine_content_root(_best_content_subtree(soup.body))
    return soup


def _best_content_subtree(root: Tag) -> Tag:
    """Prefer the most content-dense subtree inside a shell element."""

    container_names = {"article", "body", "div", "main", "section"}
    candidates = _collect_candidates(root, CONTENT_SELECTORS_EXACT, container_names, tier=2)
    candidates.extend(_collect_direct_candidates(root, container_names, tier=1))
    candidates.extend(_collect_candidates(root, CONTENT_SELECTORS_FALLBACK, container_names, tier=0))
    candidates.extend(_collect_dense_descendants(root, container_names, max_depth=5))
    if candidates:
        candidate = _pick_best_candidate(root, candidates)
        if candidate is not None:
            return candidate
    return root


def _refine_content_root(root: Tag, max_depth: int = 4) -> Tag:
    """Walk down one more level when a selected shell still contains a better content subtree."""

    current = root
    current_words = len(current.get_text(" ", strip=True).split())
    for _ in range(max_depth):
        sneak_peek = current.select_one(".post-sneak-peek")
        if isinstance(sneak_peek, Tag) and sneak_peek is not current:
            candidate = sneak_peek
            candidate_words = len(candidate.get_text(" ", strip=True).split())
            if candidate_words >= 20:
                current = candidate
                current_words = candidate_words
                continue
        else:
            shell_child = _best_page_shell_child(current)
            candidate = shell_child or _best_content_subtree(current)
            if shell_child is not None and candidate is shell_child and _looks_like_page_shell(candidate):
                deeper_candidate = _best_content_subtree(candidate)
                if deeper_candidate is not candidate and not _looks_like_chrome(deeper_candidate):
                    candidate_words = len(candidate.get_text(" ", strip=True).split())
                    deeper_words = len(deeper_candidate.get_text(" ", strip=True).split())
                    if deeper_words >= 20 and deeper_words >= candidate_words * 0.6:
                        candidate = deeper_candidate
        if candidate is current:
            break
        if _has_detached_title(current, candidate):
            break
        if candidate.name in {"p", "li", "span"}:
            break
        if _looks_like_layout_shell(candidate):
            break
        candidate_words = len(candidate.get_text(" ", strip=True).split())
        if candidate_words < 20:
            break
        if current_words and candidate_words < current_words * 0.75:
            break
        current = candidate
        current_words = candidate_words
    return current


def _root_selectors(prefer_article_body: bool) -> tuple[str, ...]:
    """Return the ordered selector list used to pick the page shell."""

    selectors = list(ROOT_SELECTORS)
    post_index = selectors.index(".post-body")
    article_index = selectors.index(".articlebody")
    if not prefer_article_body:
        selectors[post_index], selectors[article_index] = selectors[article_index], selectors[post_index]
    return tuple(selectors)


def _collect_root_candidates(soup: BeautifulSoup, selectors: tuple[str, ...]) -> list[tuple[Tag, float, int]]:
    """Collect the best candidate subtree for each matching shell."""

    candidates: dict[int, tuple[Tag, float, int]] = {}
    best_content_by_root: dict[int, Tag] = {}
    chrome_by_node: dict[int, bool] = {}
    for selector_index, root in _select_in_selector_order(soup, selectors):
        root_id = id(root)
        if root_id not in chrome_by_node:
            chrome_by_node[root_id] = _looks_like_chrome(root)
        if chrome_by_node[root_id]:
            continue
        selector_weight = _root_selector_weight(selectors[selector_index])
        root_entry = (root, selector_weight * 0.9, selector_index)
        previous = candidates.get(root_id)
        if previous is None or (root_entry[1], -root_entry[2]) > (previous[1], -previous[2]):
            candidates[root_id] = root_entry

        if root_id not in best_content_by_root:
            best_content_by_root[root_id] = _best_content_subtree(root)
        candidate = best_content_by_root[root_id]
        candidate_id = id(candidate)
        if candidate_id not in chrome_by_node:
            chrome_by_node[candidate_id] = _looks_like_chrome(candidate)
        if chrome_by_node[candidate_id]:
            continue
        subtree_entry = (candidate, selector_weight, selector_index)
        previous = candidates.get(candidate_id)
        if previous is None or (subtree_entry[1], -subtree_entry[2]) > (previous[1], -previous[2]):
            candidates[candidate_id] = subtree_entry
    return list(candidates.values())


def _collect_candidates(
    root: Tag, selectors: tuple[str, ...], container_names: set[str], tier: int
) -> list[tuple[Tag, int, int]]:
    """Collect unique content candidates for a given selector tier."""

    candidates: list[tuple[Tag, int, int]] = []
    seen: set[int] = set()
    if root.name in container_names:
        candidates.append((root, tier - 1, -1))
        seen.add(id(root))
    for selector_index, node in _select_in_selector_order(root, selectors):
        if node.name in container_names and id(node) not in seen:
            candidates.append((node, tier, selector_index))
            seen.add(id(node))
    return candidates


def _select_in_selector_order(root: Tag, selectors: tuple[str, ...]) -> list[tuple[int, Tag]]:
    """Select matching tags in the selector and document order used by repeated select calls."""

    if not selectors:
        return []
    matches_by_selector: list[list[Tag]] = [[] for _ in selectors]
    class_selectors: dict[str, list[int]] = {}
    id_selectors: dict[str, list[int]] = {}
    tag_selectors: dict[str, list[int]] = {}
    role_selectors: dict[str, list[int]] = {}
    tag_class_selectors: dict[str, list[tuple[int, str]]] = {}
    class_substrings: list[tuple[int, str]] = []
    id_substrings: list[tuple[int, str]] = []
    fallback_selectors: list[tuple[int, str]] = []
    for selector_index, selector in enumerate(selectors):
        if selector.startswith("[class*='") and selector.endswith("']"):
            class_substrings.append((selector_index, selector[len("[class*='") : -2]))
        elif selector.startswith("[id*='") and selector.endswith("']"):
            id_substrings.append((selector_index, selector[len("[id*='") : -2]))
        elif selector.startswith("[role='") and selector.endswith("']"):
            role_selectors.setdefault(selector[len("[role='") : -2], []).append(selector_index)
        elif selector.startswith("#"):
            id_selectors.setdefault(selector[1:], []).append(selector_index)
        elif selector.startswith("."):
            class_selectors.setdefault(selector[1:], []).append(selector_index)
        elif "." in selector:
            tag_name, class_name = selector.split(".", 1)
            tag_class_selectors.setdefault(tag_name, []).append((selector_index, class_name))
        elif selector.isalpha():
            tag_selectors.setdefault(selector.lower(), []).append(selector_index)
        else:
            fallback_selectors.append((selector_index, selector))

    for node in root.descendants:
        if not isinstance(node, Tag):
            continue
        tag_name = node.name
        for selector_index in tag_selectors.get(tag_name, ()):
            matches_by_selector[selector_index].append(node)
        raw_classes = node.get("class") or ()
        classes = raw_classes if isinstance(raw_classes, (list, tuple)) else str(raw_classes).split()
        for class_name in set(classes):
            for selector_index in class_selectors.get(str(class_name), ()):
                matches_by_selector[selector_index].append(node)
        identifier = str(node.get("id") or "")
        for selector_index in id_selectors.get(identifier, ()):
            matches_by_selector[selector_index].append(node)
        role = node.get("role")
        if isinstance(role, str):
            for selector_index in role_selectors.get(role, ()):
                matches_by_selector[selector_index].append(node)
        for selector_index, class_name in tag_class_selectors.get(tag_name, ()):
            if class_name in classes:
                matches_by_selector[selector_index].append(node)
        if class_substrings:
            class_value = " ".join(str(value) for value in classes)
            for selector_index, value in class_substrings:
                if value in class_value:
                    matches_by_selector[selector_index].append(node)
        if id_substrings:
            for selector_index, value in id_substrings:
                if value in identifier:
                    matches_by_selector[selector_index].append(node)
        for selector_index, selector in fallback_selectors:
            if soupsieve.match(selector, node):
                matches_by_selector[selector_index].append(node)
    return [(selector_index, node) for selector_index, matches in enumerate(matches_by_selector) for node in matches]


def _collect_direct_candidates(root: Tag, container_names: set[str], tier: int) -> list[tuple[Tag, int, int]]:
    """Collect direct child container nodes when selector matching is too weak."""

    candidates: list[tuple[Tag, int, int]] = []
    seen: set[int] = set()
    for index, node in enumerate(root.find_all(recursive=False)):
        if (
            isinstance(node, Tag)
            and node.name in REFINABLE_CHILD_TAGS
            and (node.name in container_names or _is_dense_content(node))
        ):
            if id(node) in seen:
                continue
            candidates.append((node, tier, index))
            seen.add(id(node))
    return candidates


def _collect_dense_descendants(
    root: Tag, container_names: set[str], max_depth: int, tier: int = 0
) -> list[tuple[Tag, int, int]]:
    """Collect deeper content-like descendants when selector matching misses the article body."""

    candidates: list[tuple[Tag, int, int]] = []
    seen: set[int] = set()

    def visit(node: Tag, depth: int) -> None:
        if depth > max_depth:
            return
        for index, child in enumerate(node.find_all(recursive=False)):
            if not isinstance(child, Tag):
                continue
            if _looks_like_chrome(child):
                continue
            if child.name in container_names and _is_dense_content(child):
                child_id = id(child)
                if child_id not in seen:
                    candidates.append((child, tier, depth * 10 + index))
                    seen.add(child_id)
            visit(child, depth + 1)

    visit(root, 0)
    return candidates


def _pick_best_root_candidate(candidates: list[tuple[Tag, float, int]]) -> Tag | None:
    """Return the best root candidate across all shell matches."""

    articles = {
        id(candidate): candidate
        for candidate, _, _ in candidates
        if candidate.name == "article" and _is_substantive_article(candidate)
    }
    unique_article_id = next(iter(articles)) if len(articles) == 1 else None

    ranked = sorted(
        candidates,
        key=lambda item: (
            _score_content(item[0])
            + item[1]
            + _root_candidate_penalty(item[0])
            + (350.0 if id(item[0]) == unique_article_id else 0.0),
            len(item[0].get_text(" ", strip=True)),
            -item[2],
        ),
        reverse=True,
    )
    non_body_candidates = [item for item in ranked if item[0].name != "body"]
    for candidate, _, _ in non_body_candidates or ranked:
        if not _looks_like_chrome(candidate):
            return candidate
    return None


def _is_substantive_article(candidate: Tag) -> bool:
    """Recognize a semantic article with enough editorial structure to be decisive."""

    word_count = len(candidate.get_text(" ", strip=True).split())
    paragraph_count = len(candidate.find_all("p"))
    structured_blocks = len(candidate.find_all(["table", "pre", "blockquote", "ul", "ol"]))
    return word_count >= 250 and (paragraph_count >= 4 or structured_blocks >= 2)


def _has_detached_title(root: Tag, content: Tag) -> bool:
    """Keep a short H1 sibling when refinement would otherwise discard the page title."""

    headings = root.find_all("h1")
    if len(headings) != 1 or headings[0] in content.descendants:
        return False
    heading = headings[0]
    title_branch = heading
    while isinstance(title_branch.parent, Tag) and title_branch.parent is not root:
        title_branch = title_branch.parent
    if title_branch.parent is not root or len(title_branch.get_text(" ", strip=True).split()) > 160:
        return False
    return _is_substantive_article(content)


def _detached_title_context(candidate: Tag) -> Tag | None:
    """Include a compact preceding H1 when the site stores it beside the article body."""

    has_internal_heading = candidate.find("h1") is not None
    heading = candidate.find_previous("h1") or candidate.find_next("h1")
    if not isinstance(heading, Tag) or candidate in heading.parents:
        return None
    if has_internal_heading and not any(
        isinstance(parent, Tag) and parent.name == "header" for parent in heading.parents
    ):
        return None
    candidate_ancestors = {id(node): node for node in candidate.parents if isinstance(node, Tag)}
    common: Tag | None = heading
    while common is not None and id(common) not in candidate_ancestors:
        common = common.parent if isinstance(common.parent, Tag) else None
    if common is None or common.name in {"body", "html", "[document]"}:
        return None
    title_branch = heading
    while isinstance(title_branch.parent, Tag) and title_branch.parent is not common:
        title_branch = title_branch.parent
    if title_branch.parent is not common or len(title_branch.get_text(" ", strip=True).split()) > 160:
        return None
    candidate_words = len(candidate.get_text(" ", strip=True).split())
    common_words = len(common.get_text(" ", strip=True).split())
    if candidate_words < 150 or common_words > candidate_words * 1.5 + 100:
        return None
    return common


def _root_candidate_penalty(candidate: Tag) -> float:
    """Penalize generic layout wrappers when selecting the top-level shell."""

    penalty = 0.0
    if candidate.name == "main":
        main_text_length = len(candidate.get_text(" ", strip=True))
        largest_article_length = max(
            (len(article.get_text(" ", strip=True)) for article in candidate.find_all("article")),
            default=0,
        )
        if main_text_length and largest_article_length / main_text_length >= 0.65:
            penalty -= 60.0
    if _looks_like_toc_sidebar(candidate):
        penalty -= 250.0
    if _looks_like_page_shell(candidate):
        penalty -= 120.0
    if _contains_page_shell_child(candidate):
        penalty -= 180.0
    if candidate.name not in {"article", "main"} and candidate.find("main", recursive=False) is not None:
        penalty -= 180.0
    classes = (
        candidate.get("class", []) if isinstance(candidate.get("class"), list) else [str(candidate.get("class", ""))]
    )
    marker_tokens = {token for token in " ".join(str(token).lower() for token in classes).split() if token}
    marker_tokens |= {str(candidate.get("id", "")).lower()} if candidate.get("id") else set()
    layout_tokens = {
        "container",
        "container-fluid",
        "d-flex",
        "flex-column",
        "justify-content-center",
        "justify-content-between",
        "align-items-center",
        "align-items-end",
        "row",
        "col",
        "col-12",
        "col-lg-11",
        "col-xl-9",
        "px-md-4",
        "px-xxl-5",
        "page-wrapper",
        "wrapper",
    }
    if candidate.name not in {"article", "main"} and marker_tokens & layout_tokens:
        has_embedded_main = bool(candidate.find("main", recursive=True))
        if has_embedded_main:
            penalty -= 80.0
    if marker_tokens & {"wrapper", "container-fluid", "page-wrapper"}:
        penalty -= 25.0
    penalty -= _link_density_penalty(candidate)
    return penalty


def _looks_like_toc_sidebar(candidate: Tag) -> bool:
    """Detect compact table-of-contents sidebars that should not win root selection."""

    text = candidate.get_text(" ", strip=True).lower()
    if not text:
        return False
    marker_text = " ".join(
        [str(token).lower() for token in (candidate.get("class") or ())]
        + ([str(candidate.get("id", "")).lower()] if candidate.get("id") else [])
    )
    has_toc_markers = any(token in marker_text for token in ("toc", "table-of-contents", "table_of_contents")) or (
        "table of contents" in text
    )
    if not has_toc_markers:
        return False
    if candidate.has_attr("data-toc-container") or str(candidate.get("aria-label", "")).lower() == "table of contents":
        return True
    if len(candidate.find_all("a")) > 0:
        return False
    if len(candidate.find_all(["p", "ul", "ol", "blockquote"])) > 0:
        return False
    return len(text.split()) <= 24 and len(candidate.find_all("button")) == 0


def _looks_like_layout_shell(tag: Tag) -> bool:
    """Detect generic layout wrappers that should not become the final content root."""

    classes = tag.get("class", []) if isinstance(tag.get("class"), list) else [str(tag.get("class", ""))]
    marker_tokens = {token for token in " ".join(str(token).lower() for token in classes).split() if token}
    marker_tokens |= {str(tag.get("id", "")).lower()} if tag.get("id") else set()
    return bool(marker_tokens & {"wrapper", "container-fluid", "page-wrapper"})


def _link_density_penalty(candidate: Tag) -> float:
    """Penalize non-semantic wrappers that are dominated by links instead of prose."""

    if candidate.name in {"article", "main"}:
        return 0.0
    links = len(candidate.find_all("a"))
    paragraphs = max(len(candidate.find_all("p")), 1)
    excess_links = links - (paragraphs * 5)
    if excess_links <= 0:
        return 0.0
    return min(excess_links * 1.2, 400.0)


def _pick_best_candidate(root: Tag, candidates: list[tuple[Tag, int, int]]) -> Tag | None:
    """Return the most plausible non-chrome candidate from a tier."""

    has_non_body_candidate = any(candidate.name != "body" for candidate, _, _ in candidates)
    ranked = sorted(
        candidates,
        key=lambda item: (
            _score_content(item[0])
            + (item[1] * 0.75)
            + (_root_penalty(root, item[0], len(candidates)))
            + (-1000.0 if has_non_body_candidate and item[0].name == "body" else 0.0),
            _subtree_depth(root, item[0]),
            len(item[0].get_text(" ", strip=True)),
            -item[2],
        ),
        reverse=True,
    )
    for candidate, _, _ in ranked:
        if not _looks_like_chrome(candidate):
            return candidate
    return None


def _root_selector_weight(selector: str) -> float:
    """Assign a broad specificity weight to top-level shell selectors."""

    if selector in {"article", "main", "[role='article']", "[role='main']"}:
        return 4.0
    if selector in CONTENT_SELECTORS_EXACT:
        return 2.0
    if selector in CONTENT_SELECTORS_FALLBACK:
        return 1.0
    if selector == "body":
        return -2.5
    return 0.0


def _root_penalty(root: Tag, candidate: Tag, candidate_count: int) -> float:
    """Penalize the shell node itself when a more specific descendant competes."""

    if _looks_like_page_shell(candidate):
        return -120.0
    if _contains_page_shell_child(candidate):
        return -90.0
    classes = (
        candidate.get("class", []) if isinstance(candidate.get("class"), list) else [str(candidate.get("class", ""))]
    )
    marker_tokens = {token for token in " ".join(str(token).lower() for token in classes).split() if token}
    marker_tokens |= {str(candidate.get("id", "")).lower()} if candidate.get("id") else set()
    if candidate_count > 1 and marker_tokens & {"wrapper", "container-fluid", "page-wrapper"}:
        return -25.0
    if candidate_count > 1 and candidate.name == "body":
        return -200.0
    if candidate_count > 1 and candidate is root:
        return -30.0
    return 0.0


def _is_dense_content(node: Tag) -> bool:
    """Recognize direct child wrappers that likely carry article text."""

    if not isinstance(node, Tag):
        return False
    if _looks_like_page_shell(node):
        return False
    if _contains_page_shell_child(node):
        return False
    class_text = " ".join(
        node.get("class", []) if isinstance(node.get("class"), list) else [str(node.get("class", ""))]
    ).lower()
    id_text = str(node.get("id", "")).lower()
    class_tokens = {token for token in class_text.split() if token}
    marker_tokens = class_tokens | ({id_text} if id_text else set())
    if any(token.startswith("sidebar") or token.startswith("widget") for token in marker_tokens):
        return False
    if marker_tokens & {"wrapper", "row", "sidebar", "footer", "nav", "promo"}:
        return False
    text_words = len(node.get_text(" ", strip=True).split())
    structural_children = sum(
        1
        for child in node.find_all(recursive=False)
        if isinstance(child, Tag)
        and child.name
        in {"p", "ul", "ol", "li", "figure", "table", "pre", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"}
    )
    return text_words >= 20 or structural_children >= 2


def _looks_like_page_shell(tag: Tag) -> bool:
    """Detect wrappers that mostly combine chrome around a single main body."""

    if not isinstance(tag, Tag):
        return False
    direct_child_names = {
        child.name for child in tag.find_all(recursive=False) if isinstance(child, Tag) and child.name
    }
    if tag.name in {"main", "article"}:
        return False
    chrome_names = {"header", "footer", "nav", "aside"}
    if direct_child_names & chrome_names:
        if "main" in direct_child_names:
            return True
        return any(_is_dense_content(child) for child in tag.find_all(recursive=False) if isinstance(child, Tag))
    return False


def _contains_page_shell_child(tag: Tag) -> bool:
    """Detect wrappers that contain a page-shell child instead of content directly."""

    if not isinstance(tag, Tag):
        return False
    for child in tag.find_all(recursive=False):
        if isinstance(child, Tag) and _looks_like_page_shell(child):
            return True
    return False


def _best_page_shell_child(tag: Tag) -> Tag | None:
    """Return the most plausible direct page-shell child, if one exists."""

    if not isinstance(tag, Tag):
        return None
    for child in tag.find_all(recursive=False):
        if isinstance(child, Tag) and _looks_like_page_shell(child):
            return child
    return None


def _score_content(tag: Tag) -> float:
    """Score a subtree by its likely article relevance."""

    text = tag.get_text(" ", strip=True)
    class_text = " ".join(
        tag.get("class", []) if isinstance(tag.get("class"), list) else [str(tag.get("class", ""))]
    ).lower()
    id_text = str(tag.get("id", "")).lower()
    marker_text = f"{class_text} {id_text}"
    marker_tokens = {token for token in class_text.split() if token} | ({id_text} if id_text else set())

    paragraph_count = 0
    heading_count = 0
    list_item_count = 0
    blockquote_count = 0
    table_count = 0
    row_count = 0
    image_count = 0
    pre_code_count = 0
    interactive_count = 0
    descendant_count = 0
    for descendant in tag.descendants:
        if not isinstance(descendant, Tag):
            continue
        descendant_count += 1
        name = descendant.name
        if name == "p":
            paragraph_count += 1
        elif name in _SCORE_HEADING_TAGS:
            heading_count += 1
        elif name == "li":
            list_item_count += 1
        elif name == "blockquote":
            blockquote_count += 1
        elif name == "table":
            table_count += 1
        elif name == "tr":
            row_count = min(row_count + 1, 1500)
        elif name == "img":
            image_count += 1
        elif name in _SCORE_PRE_CODE_TAGS:
            pre_code_count += 1
        if name in _SCORE_INTERACTIVE_TAGS:
            interactive_count += 1

    positive = 0.0
    positive += paragraph_count * 4.0
    positive += heading_count * 5.0
    positive += list_item_count * 2.5
    positive += blockquote_count * 3.0
    positive += table_count * 6.0
    # Long data tables are substantive article content even when most cells
    # link to primary references (e.g. vulnerability catalogs). Count rows so
    # their markup/link volume does not make the surrounding article lose to
    # a short comments or navigation block.
    positive += row_count * 1.0
    positive += image_count * 3.0
    positive += pre_code_count * 2.0
    positive += min(len(text) / 400.0, 12.0)

    if any(
        marker in marker_text
        for marker in (
            "markdown-body",
            "articlebody",
            "post-body",
            "entry-content",
            "blog-content",
            "post-content",
            "story-body",
            "content-body",
            "bodytext",
            "hb-content__text",
            "s-blog-post__body",
        )
    ):
        positive += 10.0
    elif any(
        token
        and not token.startswith("site-")
        and (token == "content" or token.endswith(("-content", "_content", "__content")))
        for token in marker_tokens
    ):
        positive += 6.0
    elif "article" in marker_text:
        positive += 6.0
    elif "post" in marker_text:
        positive += 4.0

    noise = 0.0
    noise += interactive_count * 0.3
    if "row" in marker_tokens:
        noise += 8.0
    if any(
        marker in marker_text
        for marker in (
            "share",
            "social",
            "breadcrumb",
            "related",
            "recommend",
            "newsletter",
            "subscribe",
            "promo",
            "debug",
            "cta",
            "widget",
            "sidebar",
            "nav",
            "footer",
            "tags",
            "postmeta",
            "story-title",
            "post-head",
            "author",
            "bio",
            "profile",
            "hero",
            "lead",
            "deck",
            "standfirst",
            "teaser",
            "excerpt",
            "card",
            "feature",
        )
    ):
        noise += 10.0
    noise += descendant_count * 0.08

    return positive - noise


def _subtree_depth(root: Tag, tag: Tag) -> int:
    """Return how deeply nested a candidate is inside the chosen shell."""

    depth = 0
    current = tag
    while current is not root and current.parent is not None:
        depth += 1
        parent = current.parent
        if not isinstance(parent, Tag):
            break
        current = parent
    return depth


def _looks_like_chrome(tag: Tag) -> bool:
    """Identify obvious page chrome from class or id markers."""

    classes = tag.get("class", []) if isinstance(tag.get("class"), list) else [str(tag.get("class", ""))]
    class_text = " ".join(classes).lower()
    id_text = str(tag.get("id", "")).lower()
    marker_text = f"{class_text} {id_text}".strip()
    marker_tokens = {token for token in class_text.split() if token} | ({id_text} if id_text else set())
    exact_layout_markers = {"sidebar", "footer", "header", "nav", "promo", "has-sidebar", "wp-block-list"}
    if tag.name in {"header", "nav"}:
        return True
    if any(token.startswith("sidebar") or token.startswith("widget") for token in marker_tokens):
        return True
    if any(token == "menu" or token.endswith("-menu") or token.startswith("menu-") for token in marker_tokens):
        return True
    if marker_tokens & exact_layout_markers:
        return True
    if _looks_like_tabbed_widget(tag):
        return True
    if _looks_like_tag_cloud(tag, marker_text):
        return True
    is_semantic_notice = tag.name in {"article", "main"} and any(token.startswith("notice-") for token in marker_tokens)
    return any(
        marker in marker_text
        for marker in NOISE_MARKERS
        if marker not in exact_layout_markers and not (is_semantic_notice and marker == "notice")
    )


def _looks_like_tabbed_widget(tag: Tag) -> bool:
    """Detect tabbed marketing widgets that often masquerade as content."""

    if not isinstance(tag, Tag):
        return False

    tab_markers = (
        "tabs",
        "tabs-content",
        "tabs-nav",
        "tab-content",
        "tab-content-inner",
        "tab-content-row",
        "tab-content-col",
        "tab-main",
        "tab-section",
        "tab-wrap",
    )

    def _marker_text(node: Tag) -> str:
        classes = node.get("class", []) if isinstance(node.get("class"), list) else [str(node.get("class", ""))]
        class_text = " ".join(str(value).lower() for value in classes)
        id_text = str(node.get("id", "")).lower()
        return f"{class_text} {id_text}".strip()

    node_text = _marker_text(tag)
    if any(marker in node_text for marker in tab_markers):
        return True

    for child in tag.find_all(recursive=False):
        if not isinstance(child, Tag):
            continue
        child_text = _marker_text(child)
        if any(marker in child_text for marker in tab_markers):
            return True
    return False


def _looks_like_tag_cloud(tag: Tag, marker_text: str) -> bool:
    """Detect tag clouds or label widgets that are mostly link lists."""

    if tag.name not in {"ul", "ol", "div", "nav"}:
        return False
    link_count = len(tag.find_all("a"))
    if link_count < 12:
        return False
    paragraph_count = len(tag.find_all("p"))
    heading_count = len(tag.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
    if paragraph_count > 0 or heading_count > 0:
        return False
    if any(
        marker in marker_text
        for marker in ("label-widget-content", "list-label-widget-content", "tag-cloud", "tags", "label-cloud")
    ):
        return True
    parent = tag.parent if isinstance(tag.parent, Tag) else None
    if parent is None:
        return False
    parent_classes = (
        parent.get("class", []) if isinstance(parent.get("class"), list) else [str(parent.get("class", ""))]
    )
    parent_marker_text = " ".join(str(token).lower() for token in parent_classes)
    if parent.get("id"):
        parent_marker_text = f"{parent_marker_text} {str(parent.get('id')).lower()}".strip()
    return any(
        marker in parent_marker_text
        for marker in ("widget-content", "label-widget-content", "list-label-widget-content", "tag-cloud", "tags")
    )
