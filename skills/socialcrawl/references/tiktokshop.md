# TikTok Shop

5 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 5 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/tiktokshop/product — 1 credit (standard)

Get TikTok Shop product details

- `url` (required) — Full URL of the TikTok Shop product page
- `region` (optional, string) — Region the proxy will be set to so you can access products from that country. Use 2 letter country codes like US, GB, FR, etc. For England, don't use UK, use GB.

```bash
curl "https://www.socialcrawl.dev/v1/tiktokshop/product?url=https://www.tiktok.com/shop/pdp/goli-ashwagandha-gummies-with-vitamin-d-ksm-66-vegan-non-gmo/1729587769570529799" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktokshop/product/reviews — 1 credit (standard)

List TikTok Shop product reviews

- `url` (optional, string) — Full URL of the TikTok Shop product page
- `product_id` (optional, string) — The ID of the product (required if url is not provided)
- `region` (optional, string) — ISO 3166-1 alpha-2 region for the product (e.g. `US`). Important when the product is regionally scoped.

**At least one of `url` / `product_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/tiktokshop/product/reviews" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktokshop/products — 1 credit (standard)

List TikTok Shop products

- `url` (required) — Full URL of the TikTok Shop page
- `sort_by` (optional, enum: top | new_releases) — Sort products by best-selling (`top`) or newest (`new_releases`). Defaults to `top`.
- `region` (optional, enum: US | GB | DE | FR | IT | ID | MY | MX | PH | SG | ES | TH | VN | BR | JP | IE) — Region to get shop products from. Defaults to US if not provided.

```bash
curl "https://www.socialcrawl.dev/v1/tiktokshop/products?url=https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktokshop/search — 1 credit (standard)

Search TikTok Shop products

- `query` (required) — Search keyword or phrase to find TikTok Shop products
- `page` (optional, integer) — Page number to retrieve
- `region` (optional, enum: US | GB | DE | FR | IT | ID | MY | MX | PH | SG | ES | TH | VN | BR | JP | IE) — Region to search shop products in.

```bash
curl "https://www.socialcrawl.dev/v1/tiktokshop/search?query=phone case" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktokshop/user/showcase — 1 credit (standard)

List TikTok user showcase products

- `handle` (required) — The handle of the user
- `region` (optional, string) — Region to put the proxy in
- `cursor` (optional, string) — The cursor to the next page of products

```bash
curl "https://www.socialcrawl.dev/v1/tiktokshop/user/showcase?handle=mrtiktokreviews" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
