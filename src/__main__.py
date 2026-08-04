"""Furniture.com pricing scraper (Apify Actor, Python SDK).

furniture.com is a Next.js aggregator that links out to partner stores
(casagear, lexmod, roomstogo, midinmod, zuomod, onekingslane, simpli-home, ...).

The pure extraction logic lives in src/extractor.py (no third-party deps, so it
is unit-testable in isolation — see tests/test_extract.py). This module only
wires the crawler to Apify's dataset.

We use crawlee's HttpCrawler (not BeautifulSoupCrawler) because furniture.com
embeds its product records as double-escaped JSON inside a <script> tag in the
raw HTML response. Reading context.http_response gives us the exact bytes our
regex in extractor.py expects.
"""

import crawlee
from apify import Actor
from crawlee.crawlers import HttpCrawler, HttpCrawlingContext

from .extractor import extract_products


async def main() -> None:
    await Actor.init()
    try:
        actor_input = await Actor.get_input() or {}
        start_urls = [u["url"] for u in actor_input.get("startUrls", [])] or ["https://www.furniture.com/"]
        max_pages = int(actor_input.get("maxPagesPerCrawl", 50))
        max_concurrency = int(actor_input.get("maxConcurrency", 5))
        follow_pagination = bool(actor_input.get("followPagination", True))

        # Wire up the proxy selected via the input schema's proxy editor.
        # apify 4.x: keyword-only, proxy dict goes in `actor_proxy_input`.
        proxy_config = await Actor.create_proxy_configuration(
            actor_proxy_input=actor_input.get("proxyConfiguration")
        )

        request_manager = await Actor.open_request_queue()
        await request_manager.add_requests(start_urls)
        dataset = await Actor.open_dataset()
        crawler = HttpCrawler(
            request_manager=request_manager,
            max_requests_per_crawl=max_pages,
            concurrency_settings=crawlee.ConcurrencySettings(
                max_concurrency=max_concurrency, desired_concurrency=max_concurrency
            ),
            proxy_configuration=proxy_config,
        )

        @crawler.router.default_handler
        async def handle_listing(context: HttpCrawlingContext) -> None:
            context.log.info(f"Processing {context.request.url}")
            # Raw HTML carries the RSC payload with embedded product records.
            html = (await context.http_response.read()).decode("utf-8", "replace")
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
    finally:
        # Explicit, clean shutdown (avoids the benign asyncio teardown race that
        # the `async with Actor:` context manager can trigger on sys.exit).
        await Actor.exit()



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
