# History


## 0.3.9 (2026-11-19)


* Add declarative extraction criteria for supported sites and route known-site extraction through the shared Apply pipeline, while keeping Discover as the fallback for unknown sites.
* Improve exact Discover-to-Apply replay, selector application diagnostics, and content-retention metrics.
* Add reusable criteria operations for ordered include fallback and text filtering, and improve cleanup of article chrome and promotional content.
* Improve preservation of article titles, body content, images, code, tables, and mixed document structures across real-world pages.
* Expand regression and coverage tests for site criteria, replay, and extraction behavior.


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
