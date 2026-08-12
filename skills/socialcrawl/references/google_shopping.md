# Google Shopping

4 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 3 standard (1 credit), 1 advanced (5) — the exact cost is in each endpoint heading below.

**Latency:** All Google Shopping endpoints are task-polled upstream — expect ~10–45s responses. Use a 60s timeout.

**Two-step:** `product`, `reviews`, and `sellers` need a product id (`product_id`/`gid`) obtained from `product-search` first.

## GET /v1/google_shopping/product-search — 5 credits (advanced)

Search Google Shopping products

- `query` (required) — Product search keyword (e.g. 'wireless earbuds').
- `country` (optional, string) — DataForSEO location name (e.g. 'United States', 'United Kingdom'). Defaults to United States.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to en.
- `depth` (optional, integer) — Number of product results to retrieve (default 40, max 120). More results = longer task time.
- `price_min` (optional, string) — Minimum product price filter.
- `price_max` (optional, string) — Maximum product price filter.
- `sort_by` (optional, enum: review_score | price_low_to_high | price_high_to_low) — Result ordering: review_score, price_low_to_high, or price_high_to_low.

```bash
curl "https://www.socialcrawl.dev/v1/google_shopping/product-search?query=wireless earbuds" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_shopping/product — 1 credit (standard)

Get Google Shopping product detail

- `product_id` (optional, string) — Google Shopping product_id (from product-search).
- `gid` (optional, string) — Google Shopping gid (from product-search).
- `data_docid` (optional, string) — Google Shopping data_docid (from product-search).
- `country` (optional, string) — DataForSEO location name. Defaults to United States.
- `language` (optional, string) — Language code. Defaults to en.

**At least one of `product_id` / `gid` / `data_docid` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/google_shopping/product" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_shopping/reviews — 1 credit (standard)

Get Google Shopping product reviews

- `gid` (required) — Google Shopping gid of the product (from product-search). Required.
- `product_id` (optional, string) — Google Shopping product_id (recommended for accuracy).
- `data_docid` (optional, string) — Google Shopping data_docid (recommended for accuracy).
- `depth` (optional, integer) — Number of reviews to retrieve (default 10, multiples of 10, max 8000).
- `country` (optional, string) — DataForSEO location name. Defaults to United States.
- `language` (optional, string) — Language code. Defaults to en.

```bash
curl "https://www.socialcrawl.dev/v1/google_shopping/reviews?gid=3591805395819257241" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_shopping/sellers — 1 credit (standard)

Get Google Shopping sellers for a product

- `product_id` (optional, string) — Google Shopping product_id (from product-search).
- `gid` (optional, string) — Google Shopping gid (from product-search).
- `data_docid` (optional, string) — Google Shopping data_docid (from product-search).
- `country` (optional, string) — DataForSEO location name. Defaults to United States.
- `language` (optional, string) — Language code. Defaults to en.

**At least one of `product_id` / `gid` / `data_docid` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/google_shopping/sellers" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
