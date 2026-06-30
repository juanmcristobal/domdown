from __future__ import annotations

from .domain import DomainAdapterSpec, make_domain_adapter

MEDIUM_SPEC = DomainAdapterSpec(
    name="medium",
    site_names=("Medium",),
    host_exact=("medium.com",),
    host_suffixes=(".medium.com",),
    remove_selectors=(
        "header",
        "nav",
        "footer",
        "aside",
    ),
    trim_before_first_heading=True,
    leading_noise_lines=(
        "press enter or click to view image in full size",
        "·",
        "--",
    ),
    leading_noise_prefixes=(
        "lab-",
        "category:",
        "difficulty:",
    ),
    leading_noise_patterns=(
        r"^[A-Za-z][A-Za-z0-9\s,'’/&\-:]+[—-]\s*[A-Z][A-Z ]+$",
        r"^## \*\*Author:\*\* .*$",
        r"^\[!\[.*\]\(https://miro\.medium\.com/.*\)\]\(https?://[^)]+source=post_page---byline--[^)]+\)$",
        r"^\[.*\]\(https?://[^)]+source=post_page---byline--[^)]+\)$",
        r"^\[!\[.*\]\(https://miro\.medium\.com/.*\)\]\(https://medium\.com/@[^)]+\)$",
        r"^\[.*\]\(https://medium\.com/@[^)]+\)$",
        r"^\d+\s+min read$",
        r"^Just now$",
        r"^(?:\d+\s+)?(?:second|minute|hour|day|week|month|year)s? ago$",
        r"^[A-Z][a-z]{2,8} \d{1,2}, \d{4}$",
    ),
    leading_block_patterns=(
        r"^Access Control Vulnerabilities\s+[—-]\s+APPRENTICE$",
        r"^Lab-[A-Za-z0-9].*$",
    ),
    rstrip_noise_lines=(
        "Bug Bounty",
        "Writeup",
        "Cybersecurity",
        "Penetration Testing",
        "Web Penetration Testing",
    ),
    trailing_noise_prefixes=(
        "- **Help:**",
        "- **Status:**",
        "- **About:**",
        "- **Careers:**",
        "- **Press:**",
        "- **Blog:**",
        "- **Store:**",
        "- **Privacy:**",
        "- **Rules:**",
        "- **Terms:**",
        "- **Text to speech:**",
    ),
    trailing_noise_patterns=(
        r"^\[!\[.*\]\(https://miro\.medium\.com/.*\)\]\(https?://[^)]+source=post_page---post_author_info--[^)]+\)$",
        r"^\[!\[.*\]\(https://miro\.medium\.com/.*\)\]\(https?://[^)]+source=post_page---post_publication_info--[^)]+\)$",
        r"^\[\d+ following\]\(https?://[^)]+source=post_page---post_author_info--[^)]+\)$",
    ),
    noise_lines=("·", "--"),
    noise_patterns=(
        r"^\[!\[.*\]\(https://miro\.medium\.com/.*\)\]\(https?://[^)]+source=post_page---byline--[^)]+\)$",
        r"^\[.*\]\(https?://[^)]+source=post_page---byline--[^)]+\)$",
        r"^\d+\s+min read$",
        r"^Just now$",
        r"^(?:\d+\s+)?(?:second|minute|hour|day|week|month|year)s? ago$",
        r"^[A-Z][a-z]{2,8} \d{1,2}, \d{4}$",
    ),
)

MediumAdapter = make_domain_adapter(MEDIUM_SPEC)
