"""Tests for the furniture.com pricing extractor.

Uses a committed live HTML fixture (tests/fixtures/furniture_home.html) so the
suite is repeatable and does not hit the network.
"""

import os
import json
import pytest

from src.extractor import extract_products, _clean_url

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "furniture_home.html")
SOURCE = "https://www.furniture.com/"


@pytest.fixture(scope="module")
def html():
    with open(FIXTURE, encoding="utf-8") as f:
        return f.read()


def test_fixture_present_and_reasonable(html):
    assert len(html) > 100_000, "fixture looks too small to be a real page"


def test_extracts_products(html):
    rows = extract_products(html, SOURCE)
    assert len(rows) >= 10, f"expected >=10 products, got {len(rows)}"
    assert len(rows) == 16, f"fixture should yield 16 known products, got {len(rows)}"


def test_field_types(html):
    rows = extract_products(html, SOURCE)
    for r in rows:
        assert isinstance(r["price"], float)
        assert r["salePrice"] is None or isinstance(r["salePrice"], float)
        assert isinstance(r["inStock"], str) and r["inStock"]
        assert r["variationGroupId"]
        assert r["productUrl"].startswith("http")
        assert r["sourceUrl"] == SOURCE
        assert r["scrapedAt"]
        if r["averageRating"] is not None:
            assert isinstance(r["averageRating"], float)
        if r["totalRatings"] is not None:
            assert isinstance(r["totalRatings"], int)


def test_sale_discount_is_below_list(html):
    rows = extract_products(html, SOURCE)
    discounts = [r for r in rows if r["salePrice"] is not None and r["salePrice"] < r["price"]]
    assert discounts, "fixture should contain at least one item on sale"
    for r in discounts:
        assert 0 <= r["salePrice"] < r["price"]


def test_no_duplicate_variation_ids(html):
    rows = extract_products(html, SOURCE)
    ids = [r["variationGroupId"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate variationGroupId detected"


def test_clean_url_unescapes():
    assert _clean_url("https:\\/\\/x.com\\/a") == "https://x.com/a"
    assert _clean_url('a\\"b') == 'a"b'


def test_extract_on_empty_html():
    assert extract_products("", SOURCE) == []
