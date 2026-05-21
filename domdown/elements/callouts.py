from __future__ import annotations

import re
from typing import Set

from bs4 import BeautifulSoup, Tag

from domdown.utils.dom import transfer_content


def _create_callout(soup_or_doc: BeautifulSoup, callout_type: str, title: str, content_source: Tag) -> Tag:
    callout = soup_or_doc.new_tag("div")
    callout["data-callout"] = callout_type
    callout["class"] = "callout"

    title_div = soup_or_doc.new_tag("div")
    title_div["class"] = "callout-title"
    title_inner = soup_or_doc.new_tag("div")
    title_inner["class"] = "callout-title-inner"
    title_inner.string = title
    title_div.append(title_inner)
    callout.append(title_div)

    content_div = soup_or_doc.new_tag("div")
    content_div["class"] = "callout-content"
    transfer_content(content_source, content_div)
    callout.append(content_div)

    return callout


def _get_soup(el: Tag) -> BeautifulSoup:
    node = el
    while node.parent is not None:
        node = node.parent
    if isinstance(node, BeautifulSoup):
        return node
    return BeautifulSoup(str(node), "lxml")


def standardize_callouts(element: Tag) -> None:
    soup = _get_soup(element)

    obsidian_collapsed = element.select(".callout.is-collapsed, .callout.is-collapsible")
    for el in obsidian_collapsed:
        classes = el.get("class", [])
        if isinstance(classes, list):
            is_collapsed = "is-collapsed" in classes
            el["class"] = [c for c in classes if c not in ("is-collapsed", "is-collapsible")]
        else:
            is_collapsed = False
            el["class"] = [classes]

        if not el.get("data-callout-fold"):
            el["data-callout-fold"] = "-" if is_collapsed else "+"

        fold = el.select_one(".callout-fold")
        if fold:
            fold.decompose()

        content = el.select_one(".callout-content")
        if content:
            style = content.get("style", "")
            if style:
                cleaned = re.sub(r"display\s*:\s*none\s*;?", "", style, flags=re.IGNORECASE).strip()
                if cleaned:
                    content["style"] = cleaned
                else:
                    del content["style"]

    github_alerts = element.select(".markdown-alert")
    for el in github_alerts:
        classes = el.get("class", [])
        if isinstance(classes, str):
            classes = [classes]
        type_class = next((c for c in classes if c.startswith("markdown-alert-") and c != "markdown-alert"), None)
        callout_type = type_class.replace("markdown-alert-", "") if type_class else "note"
        title = callout_type[0].upper() + callout_type[1:] if callout_type else "Note"

        title_el = el.select_one(".markdown-alert-title")
        if title_el:
            title_el.decompose()

        new_callout = _create_callout(soup, callout_type, title, el)
        el.replace_with(new_callout)

    callout_asides = element.select('aside[class*="callout"]')
    for el in callout_asides:
        classes = el.get("class", [])
        if isinstance(classes, str):
            classes = [classes]
        type_class = next((c for c in classes if c.startswith("callout-")), None)
        callout_type = type_class.replace("callout-", "") if type_class else "note"
        title = callout_type[0].upper() + callout_type[1:] if callout_type else "Note"

        content_el = el.select_one(".callout-content")
        new_callout = _create_callout(soup, callout_type, title, content_el or el)
        el.replace_with(new_callout)

    admonition_types: Set[str] = {
        "info",
        "warning",
        "note",
        "tip",
        "danger",
        "caution",
        "important",
        "abstract",
        "success",
        "question",
        "failure",
        "bug",
        "example",
        "quote",
    }
    admonitions = element.select(".admonition")
    for el in admonitions:
        if el.get("data-callout"):
            continue

        classes = el.get("class", [])
        if isinstance(classes, str):
            classes = [classes]
        callout_type = next((c for c in classes if c in admonition_types), "note")
        if not isinstance(callout_type, str):
            callout_type = "note"

        title_el = el.select_one(".admonition-title")
        title = ""
        if title_el:
            title = title_el.get_text().strip()
            title_el.decompose()
        if not title:
            title = callout_type[0].upper() + callout_type[1:]

        content_el = el.select_one(".admonition-content") or el.select_one(".details-content") or el

        new_callout = _create_callout(soup, callout_type, title, content_el)
        el.replace_with(new_callout)

    bootstrap_alerts = element.select('.alert[class*="alert-"]')
    for el in bootstrap_alerts:
        classes = el.get("class", [])
        if isinstance(classes, str):
            classes = [classes]
        type_class = next(
            (c for c in classes if c.startswith("alert-") and c != "alert-dismissible"),
            None,
        )
        callout_type = type_class.replace("alert-", "") if type_class else "note"

        title_el = el.select_one(".alert-heading, .alert-title")
        title = ""
        if title_el:
            title = title_el.get_text().strip()
            title_el.decompose()
        if not title:
            title = callout_type[0].upper() + callout_type[1:]

        new_callout = _create_callout(soup, callout_type, title, el)
        el.replace_with(new_callout)
