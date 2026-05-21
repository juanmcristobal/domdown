import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup, Tag

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


@pytest.fixture
def soup():
    def _parse(html: str) -> Tag:
        return BeautifulSoup(html, "lxml")

    return _parse
