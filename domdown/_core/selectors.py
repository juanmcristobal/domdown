"""SoupSieve selector compatibility helpers."""

from __future__ import annotations


def normalize_selector(selector: str) -> str:
    """Translate SoupSieve's deprecated ``:contains()`` alias without changing quoted text."""

    if ":contains" not in selector.lower():
        return selector

    parts: list[str] = []
    quote: str | None = None
    escaped = False
    index = 0
    while index < len(selector):
        char = selector[index]
        if escaped:
            parts.append(char)
            escaped = False
            index += 1
            continue
        if char == "\\":
            parts.append(char)
            escaped = True
            index += 1
            continue
        if quote is not None:
            parts.append(char)
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            parts.append(char)
            index += 1
            continue

        if selector[index : index + 9].lower() == ":contains":
            end = index + 9
            boundary = end == len(selector) or not (selector[end].isalnum() or selector[end] in "_-")
            argument = selector[end:].lstrip()
            if boundary and argument.startswith("("):
                parts.append(":-soup-contains")
                index = end
                continue

        parts.append(char)
        index += 1

    return "".join(parts)
