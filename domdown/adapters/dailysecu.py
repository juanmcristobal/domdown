from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter

DAILYSECU_SPEC = DomainAdapterSpec(
    name="dailysecu",
    site_names=("데일리시큐",),
    host_exact=("dailysecu.com",),
    host_suffixes=(".dailysecu.com",),
    remove_selectors=(),
    noise_lines=(
        "산업",
        "글자크기 설정",
        "가",
        "기사의 본문 내용은 이 글자크기로 변경됩니다.",
        "이 기사를 공유합니다",
        "[mkgil@dailysecu.com](mailto:mkgil@dailysecu.com)",
        "[다른기사 보기](https://www.dailysecu.com/news/articleList.html?sc_area=I&sc_word=mkgil&view_type=sm)",
    ),
    trailing_noise_lines=("많이 본 뉴스",),
    noise_patterns=(
        r"^!\[길민권 기자의 프로필 이미지\].*$",
        r"^\[길민권 기자\]\(https://www\.dailysecu\.com/news/articleList\.html\?.*\)$",
    ),
)

DailySecuAdapter = make_domain_adapter(DAILYSECU_SPEC)
