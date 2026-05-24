from __future__ import annotations

import pytest

from domdown.adapters.base import ArticleAdapter


def test_article_adapter_protocol_methods_raise_not_implemented_error() -> None:
    """The abstract protocol methods should remain explicitly unimplemented."""

    with pytest.raises(NotImplementedError):
        ArticleAdapter.matches(object(), None)  # type: ignore[arg-type]
    with pytest.raises(NotImplementedError):
        ArticleAdapter.preprocess(object(), None)  # type: ignore[arg-type]
    with pytest.raises(NotImplementedError):
        ArticleAdapter.refine_metadata(object(), None)  # type: ignore[arg-type]
    with pytest.raises(NotImplementedError):
        ArticleAdapter.postprocess(object(), None)  # type: ignore[arg-type]
