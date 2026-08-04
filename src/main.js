// Apify Actor entrypoint: furniture pricing data scraper.
//
// Scaffold only — replace with the actual scraper logic you built in the
// Apify web console. The structure below mirrors a standard Crawlee/Apify
// Actor: it reads input, runs a crawler, and pushes pricing records to the
// default dataset.
//
// Docs: https://sdk.apify.com/

import { Actor } from 'apify';
import { CheerioCrawler } from 'crawlee';

// Default seed URLs. Override via Actor input (startUrls).
const DEFAULT_START_URLS = [
  // Example: 'https://www.example-furniture-store.com/products?category=sofas',
];

async function main() {
  await Actor.init();

  const input = await Actor.getInput() ?? {};
  const { startUrls = DEFAULT_START_URLS, maxPagesPerCrawl = 50 } = input;

  const requestList = await Actor.openRequestList('start', startUrls);
  const dataset = await Actor.openDataset();

  const crawler = new CheerioCrawler({
    requestList,
    maxRequestsPerCrawl: maxPagesPerCrawl,
    async requestHandler({ $, request, enqueueLinks }) {
      // TODO: adapt these selectors to your target store.
      const items = [];
      $('.product').each((_, el) => {
        const $el = $(el);
        items.push({
          url: request.url,
          name: $el.find('.product-name').text().trim(),
          price: $el.find('.price').text().trim(),
          currency: 'USD',
          scrapedAt: new Date().toISOString(),
        });
      });
      await dataset.pushData(items);

      // Follow pagination / product links.
      await enqueueLinks({ selector: 'a.product, a.next' });
    },
  });

  await crawler.run();
  await Actor.exit();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
