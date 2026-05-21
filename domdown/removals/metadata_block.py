from __future__ import annotations

import re
from typing import Optional

from bs4 import Tag

DATE_RE = re.compile(
    r"\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
    r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?"
    r"|Dec(?:ember)?)\s+\d{1,2}[\s,]+\d{4}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?"
    r"|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?"
    r"|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}"
    r"|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b",
    re.IGNORECASE,
)


def _next_element_sibling(el: Tag) -> Optional[Tag]:
    sib = el.next_sibling
    while sib is not None:
        if isinstance(sib, Tag):
            return sib
        sib = sib.next_sibling
    return None


def remove_metadata_block(main_content: Tag) -> None:
    content_h1 = main_content.select_one("h1")
    if not content_h1:
        return

    sibling = _next_element_sibling(content_h1)
    for _ in range(3):
        if sibling is None:
            break
        next_sib = _next_element_sibling(sibling)
        text = (sibling.get_text() or "").strip()
        if text and len(text) < 300:
            has_date = bool(DATE_RE.search(text))
            if not has_date:
                for el in sibling.select("p, time"):
                    if DATE_RE.search((el.get_text() or "").strip()):
                        has_date = True
                        break
            if has_date:
                sibling.decompose()
                break
        sibling = next_sib
