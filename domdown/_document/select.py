from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from .._constants import CONTENT_SELECTORS_EXACT, CONTENT_SELECTORS_FALLBACK, NOISE_MARKERS, REFINABLE_CHILD_TAGS, ROOT_SELECTORS


def choose_root(soup: BeautifulSoup, prefer_article_body: bool = True) -> Tag:
    """Choose the most relevant content root from a parsed document."""

    selectors = _root_selectors(prefer_article_body)
    candidates = _collect_root_candidates(soup, selectors)
    if candidates:
        candidate = _pick_best_root_candidate(candidates)
        if candidate is not None:
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
    if candidates:
        candidate = _pick_best_candidate(root, candidates)
        if candidate is not None:
            if candidate is root and _looks_like_page_shell(root):
                shell_children = [item for item in candidates if item[0] is not root and not _looks_like_chrome(item[0])]
                if shell_children:
                    child_candidate = _pick_best_candidate(root, shell_children)
                    if child_candidate is not None:
                        return child_candidate
            return candidate
    return root


def _refine_content_root(root: Tag, max_depth: int = 4) -> Tag:
    """Walk down one more level when a selected shell still contains a better content subtree."""

    current = root
    current_words = len(current.get_text(" ", strip=True).split())
    for _ in range(max_depth):
        shell_child = _best_page_shell_child(current)
        candidate = shell_child or _best_content_subtree(current)
        if candidate is current:
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
    for selector_index, selector in enumerate(selectors):
        for root in soup.select(selector):
            if not isinstance(root, Tag) or _looks_like_chrome(root):
                continue
            selector_weight = _root_selector_weight(selector)
            root_entry = (root, selector_weight * 0.9, selector_index)
            previous = candidates.get(id(root))
            if previous is None or (root_entry[1], -root_entry[2]) > (previous[1], -previous[2]):
                candidates[id(root)] = root_entry

            candidate = _best_content_subtree(root)
            if not isinstance(candidate, Tag) or _looks_like_chrome(candidate):
                continue
            candidate_id = id(candidate)
            subtree_entry = (candidate, selector_weight, selector_index)
            previous = candidates.get(candidate_id)
            if previous is None or (subtree_entry[1], -subtree_entry[2]) > (previous[1], -previous[2]):
                candidates[candidate_id] = subtree_entry
    return list(candidates.values())


def _collect_candidates(root: Tag, selectors: tuple[str, ...], container_names: set[str], tier: int) -> list[tuple[Tag, int, int]]:
    """Collect unique content candidates for a given selector tier."""

    candidates: list[tuple[Tag, int, int]] = []
    seen: set[int] = set()
    if root.name in container_names:
        candidates.append((root, tier - 1, -1))
        seen.add(id(root))
    for selector_index, selector in enumerate(selectors):
        for node in root.select(selector):
            if isinstance(node, Tag) and node.name in container_names and id(node) not in seen:
                candidates.append((node, tier, selector_index))
                seen.add(id(node))
    return candidates


def _collect_direct_candidates(root: Tag, container_names: set[str], tier: int) -> list[tuple[Tag, int, int]]:
    """Collect direct child container nodes when selector matching is too weak."""

    candidates: list[tuple[Tag, int, int]] = []
    seen: set[int] = set()
    for index, node in enumerate(root.find_all(recursive=False)):
        if isinstance(node, Tag) and node.name in REFINABLE_CHILD_TAGS and (node.name in container_names or _is_dense_content(node)):
            if id(node) in seen:
                continue
            candidates.append((node, tier, index))
            seen.add(id(node))
    return candidates


def _pick_best_root_candidate(candidates: list[tuple[Tag, float, int]]) -> Tag | None:
    """Return the best root candidate across all shell matches."""

    ranked = sorted(
        candidates,
        key=lambda item: (
            _score_content(item[0]) + item[1] + _root_candidate_penalty(item[0]),
            len(item[0].get_text(" ", strip=True)),
            -item[2],
        ),
        reverse=True,
    )
    non_body_candidates = [item for item in ranked if item[0].name != "body"]
    for candidate, _, _ in (non_body_candidates or ranked):
        if not _looks_like_chrome(candidate):
            return candidate
    return None


def _root_candidate_penalty(candidate: Tag) -> float:
    """Penalize generic layout wrappers when selecting the top-level shell."""

    if _looks_like_page_shell(candidate):
        return -120.0
    if _contains_page_shell_child(candidate):
        return -90.0
    classes = candidate.get("class", []) if isinstance(candidate.get("class"), list) else [str(candidate.get("class", ""))]
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
            return -80.0
    if marker_tokens & {"wrapper", "container-fluid", "page-wrapper"}:
        return -25.0
    return 0.0


def _looks_like_layout_shell(tag: Tag) -> bool:
    """Detect generic layout wrappers that should not become the final content root."""

    classes = tag.get("class", []) if isinstance(tag.get("class"), list) else [str(tag.get("class", ""))]
    marker_tokens = {token for token in " ".join(str(token).lower() for token in classes).split() if token}
    marker_tokens |= {str(tag.get("id", "")).lower()} if tag.get("id") else set()
    return bool(marker_tokens & {"wrapper", "container-fluid", "page-wrapper"})


def _pick_best_candidate(root: Tag, candidates: list[tuple[Tag, int, int]]) -> Tag | None:
    """Return the most plausible non-chrome candidate from a tier."""

    ranked = sorted(
        candidates,
        key=lambda item: (
            _score_content(item[0]) + (item[1] * 0.75) + (_root_penalty(root, item[0], len(candidates))),
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
        return 3.0
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
    classes = candidate.get("class", []) if isinstance(candidate.get("class"), list) else [str(candidate.get("class", ""))]
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
    class_text = " ".join(node.get("class", []) if isinstance(node.get("class"), list) else [str(node.get("class", ""))]).lower()
    id_text = str(node.get("id", "")).lower()
    class_tokens = {token for token in class_text.split() if token}
    marker_tokens = class_tokens | ({id_text} if id_text else set())
    if marker_tokens & {"wrapper", "row", "sidebar", "footer", "nav", "promo"}:
        return False
    text_words = len(node.get_text(" ", strip=True).split())
    structural_children = sum(1 for child in node.find_all(recursive=False) if isinstance(child, Tag) and child.name in {"p", "ul", "ol", "li", "figure", "table", "pre", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"})
    return text_words >= 20 or structural_children >= 2


def _looks_like_page_shell(tag: Tag) -> bool:
    """Detect wrappers that mostly combine chrome around a single main body."""

    if not isinstance(tag, Tag):
        return False
    direct_child_names = {
        child.name
        for child in tag.find_all(recursive=False)
        if isinstance(child, Tag) and child.name
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
    class_text = " ".join(tag.get("class", []) if isinstance(tag.get("class"), list) else [str(tag.get("class", ""))]).lower()
    id_text = str(tag.get("id", "")).lower()
    marker_text = f"{class_text} {id_text}"
    marker_tokens = {token for token in class_text.split() if token} | ({id_text} if id_text else set())

    positive = 0.0
    positive += len(tag.find_all("p")) * 4.0
    positive += len(tag.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])) * 5.0
    positive += len(tag.find_all("li")) * 2.5
    positive += len(tag.find_all("blockquote")) * 3.0
    positive += len(tag.find_all("table")) * 6.0
    positive += len(tag.find_all("img")) * 3.0
    positive += len(tag.find_all(["pre", "code"])) * 2.0
    positive += min(len(text) / 400.0, 12.0)

    if any(
        marker in marker_text
        for marker in (
            "markdown-body",
            "articlebody",
            "post-body",
            "entry-content",
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
    noise += len(tag.find_all(["a", "button", "form", "iframe", "input", "select", "textarea"])) * 0.3
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
    noise += len(tag.find_all(True)) * 0.08

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
    exact_layout_markers = {"sidebar", "footer", "nav", "promo", "has-sidebar", "wp-block-list"}
    if marker_tokens & exact_layout_markers:
        return True
    return any(marker in marker_text for marker in NOISE_MARKERS if marker not in exact_layout_markers)
