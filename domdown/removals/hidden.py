from __future__ import annotations

import re
from typing import List, Optional

from bs4 import Tag

from domdown.types import DebugRemoval
from domdown.utils import log_debug, text_preview
from domdown.utils.dom import has_responsive_show_class

HIDDEN_STYLE_PATTERN = re.compile(
    r"(?:^|;\s*)(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0)(?:\s*;|\s*$)",
    re.IGNORECASE,
)


def remove_hidden_elements(
    doc: Tag,
    debug: bool,
    debug_removals: Optional[List[DebugRemoval]] = None,
) -> None:
    count = 0
    elements_to_remove: list = []

    all_elements = doc.select("*")

    for element in all_elements:
        if element.select_one("math, [data-mathml], .katex-mathml") or element.name == "math":
            continue

        style = element.get("style")
        if style and isinstance(style, str) and HIDDEN_STYLE_PATTERN.search(style):
            if "display" in style:
                reason = "display:none"
            elif "visibility" in style:
                reason = "visibility:hidden"
            else:
                reason = "opacity:0"
            elements_to_remove.append((element, reason))
            count += 1
            continue

        class_attr = element.get("class")
        if not class_attr:
            continue
        if isinstance(class_attr, list):
            class_name = " ".join(class_attr)
        else:
            class_name = str(class_attr)

        if not class_name:
            continue

        tokens = class_name.split()
        if has_responsive_show_class(class_name):
            continue

        for token in tokens:
            is_exact = token == "hidden" or token == "invisible"
            is_variant = "[" not in token and (token.endswith(":hidden") or token.endswith(":invisible"))

            if is_exact or is_variant:
                elements_to_remove.append((element, f"class:{token}"))
                count += 1
                break

    for el, reason in elements_to_remove:
        if debug and debug_removals is not None:
            debug_removals.append(
                DebugRemoval(
                    step="removeHiddenElements",
                    reason=reason,
                    text=text_preview(el),
                )
            )
        el.decompose()

    log_debug(debug, "Removed hidden elements:", count=count)
