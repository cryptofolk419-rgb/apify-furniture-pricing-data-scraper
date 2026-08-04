"""Furniture.com pricing scraper (Apify Actor, Python SDK).

furniture.com is a Next.js aggregator. Each listing/category page embeds its
product records as DOUBLY JSON-escaped objects inside the React Server
Components payload (self.__next_f). We extract those records with a regex
rather than relying on fragile CSS selectors, which makes the scraper robust
to cosmetic HTML changes.

Each record gives us: price, sale_price, in_stock, variation_group_id, and
seller_pdp_url (the outbound product page on a partner store such as
casagear.com, lexmod.com, roomstogo.com, ...).
"""

import re
import json
from typing import Optional
from datetime import datetime, timezone
from urllib.parse import urljoin

from apify import Actor
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

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


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        start_urls = [u["url"] for u in actor_input.get("startUrls", [])] or ["https://www.furniture.com/"]
        max_pages = int(actor_input.get("maxPagesPerCrawl", 50))
        max_concurrency = int(actor_input.get("maxConcurrency", 5))
        follow_pagination = bool(actor_input.get("followPagination", True))

        request_list = await Actor.open_request_list("start", start_urls)
        dataset = await Actor.open_dataset()
        crawler = BeautifulSoupCrawler(
            request_list=request_list,
            max_requests_per_crawl=max_pages,
            max_concurrency=max_concurrency,
        )

        @crawler.router.default_handler
        async def handle_listing(context: BeautifulSoupCrawlingContext) -> None:
            context.log.info(f"Processing {context.request.url}")
            # Raw HTML carries the RSC payload with embedded product records.
            html = context.http_response.read().decode("utf-8", "replace")
            products = extract_products(html, context.request.url)
            if products:
                await dataset.push_data(products)
                context.log.info(f"  extracted {len(products)} products")
            else:
                context.log.warning(f"  no products found on {context.request.url}")

            if follow_pagination:
                await context.enqueue_links(
                    selector="a[href*='/products'], a[href*='?page'], a.next, a[rel='next']",
                    label="listing",
                )

        await crawler.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
