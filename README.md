# apify-furniture-pricing-data-scraper

An Apify Actor that scrapes furniture product **pricing data** from e-commerce
sites for market and competitor analysis.

> **Status:** scaffold. The crawler logic in `src/main.js` is a starter
> template — port over the actual scraper you built in the Apify web console,
> or flesh out the selectors for your target stores.

## Structure

```
apify-furniture-pricing-data-scraper/
├── package.json        # Node.js + Apify SDK deps
├── src/
│   └── main.js         # Actor entrypoint (Crawlee CheerioCrawler)
├── .gitignore
└── README.md
```

## Local development

```bash
npm install
# Run against a sample input
echo '{"startUrls":["https://example.com/products"]}' | node src/main.js
```

## Deploy to Apify

1. Push this repo to GitHub (already done).
2. In the Apify console, create an Actor from the GitHub integration, or:
   ```bash
   apify login
   apify push
   ```
3. Set Actor input (start URLs, max pages, proxy) via the console UI.

## Notes

- This scaffold uses the **Node.js / Apify SDK**. If your original scraper was
  written in **Python** (Apify SDK for Python), let me know and I'll swap the
  layout to `src/main.py` + `requirements.txt`.
- Never commit `.env` or API tokens — they're git-ignored.
