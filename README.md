# Furniture.com Pricing Scraper (Apify Actor)

An Apify Actor (Python SDK) that scrapes **furniture product pricing data**
from [furniture.com](https://www.furniture.com/) — an aggregator that links out
to partner stores (casagear, lexmod, roomstogo, midinmod, zuomod, onekingslane,
simpli-home, ...).

For every listing it extracts:

| Field             | Meaning                                              |
|-------------------|------------------------------------------------------|
| `variationGroupId`| furniture.com's product/variant ID                   |
| `price`           | List price (USD)                                      |
| `salePrice`       | Current sale price (USD), or `null` if no discount    |
| `inStock`         | Stock status string (e.g. "Ready to ship")           |
| `averageRating`   | Average star rating, or `null`                        |
| `totalRatings`    | Number of ratings, or `null`                          |
| `productUrl`      | Outbound product page on the partner store            |
| `sourceUrl`       | The furniture.com page the record was found on        |
| `scrapedAt`       | ISO timestamp                                         |

## How it works

furniture.com is a Next.js site. Its product records are embedded as
**doubly JSON-escaped objects** inside the React Server Components payload
(`self.__next_f`). Rather than depend on fragile CSS selectors, the scraper
extracts those records with a regex, so it survives cosmetic HTML changes.

## Repository layout

```
apify-furniture-pricing-data-scraper/
├── .actor/
│   ├── actor.json          # Apify Actor spec
│   └── input_schema.json   # Console input fields
├── src/
│   └── main.py             # Actor entrypoint (Crawlee BeautifulSoupCrawler)
├── Dockerfile              # Apify Python base image
├── requirements.txt
├── .gitignore
└── README.md
```

## Local development

```bash
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements.txt
# Test the extraction logic against a saved page:
python -c "import src.main as m; print(len(m.extract_products(open('page.html').read(), 'x')))"
```

## Deploy to Apify

1. Push this repo to GitHub (already done).
2. In the Apify console, create an Actor from GitHub (it reads `.actor/actor.json`).
3. Run it — default start URL is `https://www.furniture.com/`. Set pricing later
   via the Apify Store listing once the Actor is published.

## Notes / limitations

- furniture.com only exposes **listing-level** pricing. The deep product detail
  (full specs, all variants) lives on the partner store's domain; `productUrl`
  points there if you want to crawl further.
- The site is dynamic; if furniture.com changes its RSC payload shape, the regex
  in `src/main.py` (`_PRODUCT_RE`) is the single place to update.
- Always run behind Apify's residential proxy in production to avoid blocking.
