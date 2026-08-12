# Amazon

5 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 3 standard (1 credit), 2 advanced (5) — the exact cost is in each endpoint heading below.

## GET /v1/amazon/shop — 1 credit (standard)

Get Amazon shop page

- `url` (required) — Full URL of the Amazon shop or storefront page

```bash
curl "https://www.socialcrawl.dev/v1/amazon/shop?url=https://www.amazon.com/shop/sydneydelrey" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/amazon/product-search — 1 credit (standard)

Search Amazon products by keyword

- `query` (required) — Search keyword or phrase.
- `country` (optional, enum: US | GB | CA | DE | FR | IT | ES | JP | IN | MX | BR | AU | NL) — Amazon marketplace as an ISO 3166-1 alpha-2 country code (default US). Supported: US, GB, CA, DE, FR, IT, ES, JP, IN, MX, BR, AU, NL. Note: non-US marketplaces (especially EU) are best-effort — the upstream provider is slower and occasionally times out for these; such calls are refunded, and US is the most reliable marketplace.
- `depth` (optional, integer) — Maximum number of products to return (max 700). Higher depth returns more rows at the same flat credit cost.

```bash
curl "https://www.socialcrawl.dev/v1/amazon/product-search?query=wireless earbuds" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/amazon/product — 5 credits (advanced)

Get an Amazon product by ASIN

- `asin` (required) — 10-character Amazon ASIN (the product identifier).
- `country` (optional, enum: US | GB | CA | DE | FR | IT | ES | JP | IN | MX | BR | AU | NL) — Amazon marketplace as an ISO 3166-1 alpha-2 country code (default US). Supported: US, GB, CA, DE, FR, IT, ES, JP, IN, MX, BR, AU, NL. Note: non-US marketplaces (especially EU) are best-effort — the upstream provider is slower and occasionally times out for these; such calls are refunded, and US is the most reliable marketplace.

```bash
curl "https://www.socialcrawl.dev/v1/amazon/product?asin=B0FQFB8FMG" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/amazon/reviews — 5 credits (advanced)

Get Amazon product reviews

- `asin` (required) — 10-character Amazon ASIN (the product identifier).
- `country` (optional, enum: US | GB | CA | DE | FR | IT | ES | JP | IN | MX | BR | AU | NL) — Amazon marketplace as an ISO 3166-1 alpha-2 country code (default US). Supported: US, GB, CA, DE, FR, IT, ES, JP, IN, MX, BR, AU, NL. Note: non-US marketplaces (especially EU) are best-effort — the upstream provider is slower and occasionally times out for these; such calls are refunded, and US is the most reliable marketplace.

```bash
curl "https://www.socialcrawl.dev/v1/amazon/reviews?asin=B0DCH8VDXF" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/amazon/sellers — 1 credit (standard)

Get Amazon sellers and offers for a product

- `asin` (required) — 10-character Amazon ASIN (the product identifier).
- `country` (optional, enum: US | GB | CA | DE | FR | IT | ES | JP | IN | MX | BR | AU | NL) — Amazon marketplace as an ISO 3166-1 alpha-2 country code (default US). Supported: US, GB, CA, DE, FR, IT, ES, JP, IN, MX, BR, AU, NL. Note: non-US marketplaces (especially EU) are best-effort — the upstream provider is slower and occasionally times out for these; such calls are refunded, and US is the most reliable marketplace.

```bash
curl "https://www.socialcrawl.dev/v1/amazon/sellers?asin=B09SM24S8C" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
