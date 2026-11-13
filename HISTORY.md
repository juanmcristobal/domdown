# History


## 0.3.8 (2026-11-13)


* Improve generic editorial extraction and cleanup across news and security sites, including removal of campaign banners, comments, recommendations, and trailing editorial modules.
* Preserve article text marked with `toc-visible` classes and retain CISA KEV vulnerability records while removing promotional cards.
* Reduce repeated DOM and Markdown work in content selection, cleanup, metadata extraction, and rendering; streamline integration-test replay while retaining the real-document snapshots.
* Add and refine real-world regression coverage for editorial extraction, promotional content, and security articles.


## 0.3.4 (2026-07-14)


* Improve generic article chrome cleanup for blog metadata, TOCs, CTAs, and related modules.
* Improve HTML table rendering for merged cells, uneven rows, escaped pipes, and line breaks.
* Add real-world regression fixtures for Okta and Socket security articles.


## 0.1.0 (2026-05-21)


* First release.


## 0.2.0 (2026-06-03)


* Fix release workflow checkout for PyPI publish.
* Change installation instructions to use `pip install domdown` (breaking change).
