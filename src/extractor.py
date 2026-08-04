"""Pure extraction logic for furniture.com pricing data.

furniture.com is a Next.js aggregator. Each listing/category page embeds its
product records as DOUBLY JSON-escaped objects inside the React Server
Components payload (self.__next_f). We extract those records with a regex
rather than relying on fragile CSS selectors, which makes the scraper robust
to cosmetic HTML changes.

This module has NO third-party dependencies so it can be unit-tested in
isolation (see tests/test_extract.py).
"""

import re
from datetime import datetime, timezone

# Matches one embedded product record in furniture.com's RSC payload.
# The payload uses double-escaped JSON: \\"field\\":value
_PRODUCT_RE = re.compile(
    r'\\"price\\":\s*([0-9.]+),'
    r'\\"sale_price\\":\s*(null|[0-9.]+),'
    r'\\"in_stock\\":\s*\\"([^\\"]+)\\"'
    r'(?:.*?\\"average_rating\\":\s*(null|[0-9.]+))?'
    r'(?:.*?\\"total_ratings\\":\s*(null|[0-9]+))?'
    r'.*?'
    r'\\"variation_group_id\\":\s*\\"([^\\"]+)\\"'
    r'.*?'
    r'\\"seller_pdp_url\\":\s*\\"([^\\"]+)\\"',
    re.S,
)


def _clean_url(raw: str) -> str:
    """Un-escape a double-escaped JSON string URL."""
    return raw.replace('\\/', '/').replace('\\"', '"')


def extract_products(html: str, source_url: str) -> list[dict]:
    """Pull all product pricing records out of a furniture.com page."""
    rows: list[dict] = []
    for m in _PRODUCT_RE.finditer(html):
        price_raw, sale_raw, stock, avg_raw, tot_raw, vgid, url_raw = m.groups()
        rows.append({
            "sourceUrl": source_url,
            "variationGroupId": vgid,
            "price": float(price_raw),
            "salePrice": None if sale_raw == "null" else float(sale_raw),
            "inStock": stock,
            "averageRating": None if avg_raw in (None, "null") else float(avg_raw),
            "totalRatings": None if tot_raw in (None, "null") else int(tot_raw),
            "productUrl": _clean_url(url_raw),
            "scrapedAt": datetime.now(timezone.utc).isoformat(),
        })
    return rows
