from __future__ import annotations

from bs4 import Tag


def clean_root(root: Tag, remove_selectors: tuple[str, ...], skip_tags: set[str]) -> Tag:
    for selector in remove_selectors:
        for node in root.select(selector):
            node.decompose()
    for node in list(root.find_all(skip_tags)):
        node.decompose()
    for img in root.find_all("img"):
        data_src = img.get("data-src") or img.get("data-original") or img.get("data-lazy-src")
        if data_src and (not img.get("src") or str(img.get("src", "")).startswith("data:")):
            img["src"] = data_src
    return root
