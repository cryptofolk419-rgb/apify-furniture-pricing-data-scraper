# Apify Store Listing — Copy & Pricing

This file is the publish-ready listing for the Apify Store. When you publish the
Actor (from the Apify console → your Actor → Publish to Store), paste the fields
below. The long description can also be sourced from `README.md` automatically.

---

## Name (title)
Furniture.com Pricing Scraper

## Short description (≤ 120 chars)
Scrape furniture prices, discounts & stock from furniture.com — the aggregator that links to 100s of furniture stores.

## Categories
- ecommerce
- pricing
- research

## Long description (Markdown — used as the Store page body)
```
# Furniture.com Pricing Scraper

Turn furniture.com into a clean pricing dataset. This Actor extracts product
pricing, sale discounts, and stock status from furniture.com — a furniture
aggregator that surfaces listings from hundreds of partner stores (Casagear,
Lexmod, Rooms To Go, MidInMod, Zuomod, One Kings Lane, Simpli Home, and more).

## What you get
For every listing the Actor captures:
- Regular price and current sale price (USD)
- Stock status (e.g. "Ready to ship")
- Average rating and number of ratings
- The outbound product URL on the partner store
- A stable variation/product ID and the source page it came from

## Why use it
- Competitor & market price monitoring across the furniture category
- Track discount depth (sale vs. list) at scale
- Feed pricing dashboards, alerts, or downstream analytics
- Robust extraction: data is read from the page's embedded JSON payload, so it
  survives cosmetic HTML/layout changes

## How to run
1. Open the Actor and hit **Run** (default start URL is the furniture.com homepage).
2. Optionally change **Start URLs** to a specific category/listing page, raise
   **Max pages per crawl**, or turn off **Follow pagination**.
3. Results are delivered to the dataset and can be exported as JSON, CSV, Excel,
   or Google Sheets.

## Notes
- furniture.com shows **listing-level** pricing; the deep product page (full
  specs, all variants) lives on the partner store — `productUrl` points there.
- Run behind a proxy (the Actor enables Apify residential proxy by default) to
  avoid rate-limiting on larger crawls.

## Output example
{
  "variationGroupId": "CAG_UPT336139",
  "price": 831.67,
  "salePrice": 376.0,
  "inStock": "Ready to ship",
  "averageRating": null,
  "totalRatings": null,
  "productUrl": "https://www.casagear.com/products/...",
  "sourceUrl": "https://www.furniture.com/",
  "scrapedAt": "2026-08-04T12:00:00+00:00"
}
```

## Suggested pricing
Apify Store pricing is set when you publish. Recommended starting model for a
niche pricing scraper like this:

- **Model:** Monthly subscription (recommended over per-run for steady users) with
  a free/cheap trial so buyers can validate output.
- **Free trial:** First 7 days or first 100 results free.
- **Starter:** $15 / month — up to 5,000 results / month.
- **Standard:** $49 / month — up to 25,000 results / month.
- **Pro:** $99 / month — up to 100,000 results / month.
- (Alternative: transaction pricing at ~$0.50 per 1,000 results if you prefer
  pay-as-you-go; Apify takes its platform commission on top.)

Set the numbers to match your compute cost — a full-category crawl is light
(HTML only, no browser rendering), so margins are healthy at these tiers.
