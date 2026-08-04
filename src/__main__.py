"""Furniture.com pricing scraper (Apify Actor, Python SDK).

furniture.com is a Next.js aggregator that links out to partner stores
(casagear, lexmod, roomstogo, midinmod, zuomod, onekingslane, simpli-home, ...).

The pure extraction logic lives in src/extractor.py (no third-party deps, so it
is unit-testable in isolation — see tests/test_extract.py). This module only
wires the crawler to Apify's dataset.
"""

from apify import Actor
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from .extractor import extract_products


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        start_urls = [u["url"] for u in actor_input.get("startUrls", [])] or ["https://www.furniture.com/"]
        max_pages = int(actor_input.get("maxPagesPerCrawl", 50))
        max_concurrency = int(actor_input.get("maxConcurrency", 5))
        follow_pagination = bool(actor_input.get("followPagination", True))

        # Wire up the proxy selected via the input schema's proxy editor.
        proxy_config = await Actor.create_proxy_configuration(
            actor_input.get("proxyConfiguration")
        )

        request_list = await Actor.open_request_list("start", start_urls)
        dataset = await Actor.open_dataset()
        crawler = BeautifulSoupCrawler(
            request_list=request_list,
            max_requests_per_crawl=max_pages,
            max_concurrency=max_concurrency,
            proxy_configuration=proxy_config,
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
