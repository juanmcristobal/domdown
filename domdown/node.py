from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup

from domdown.domdown import Domdown as DomdownClass
from domdown.markdown import to_markdown
from domdown.types import DomdownOptions, DomdownResponse


def parse(
    html: str,
    url: str = "",
    options: Optional[DomdownOptions] = None,
) -> DomdownResponse:
    doc = BeautifulSoup(html, "lxml")
    page_url = url or "about:blank"

    opts = (
        DomdownOptions(url=page_url, **{k: v for k, v in vars(options).items() if v is not None})
        if options
        else DomdownOptions(url=page_url)
    )

    domdown = DomdownClass(doc, opts)
    result = domdown.parse()

    to_markdown(result, opts, page_url)

    return result


async def parse_async(
    html: str,
    url: str = "",
    options: Optional[DomdownOptions] = None,
) -> DomdownResponse:
    doc = BeautifulSoup(html, "lxml")
    page_url = url or "about:blank"

    opts = (
        DomdownOptions(url=page_url, **{k: v for k, v in vars(options).items() if v is not None})
        if options
        else DomdownOptions(url=page_url)
    )

    domdown = DomdownClass(doc, opts)
    result = await domdown.parse_async()

    to_markdown(result, opts, page_url)

    return result
