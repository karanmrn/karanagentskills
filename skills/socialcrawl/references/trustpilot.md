# Trustpilot

2 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit), 1 advanced (5) — the exact cost is in each endpoint heading below.

**Latency:** Trustpilot endpoints are task-polled upstream — expect ~10–45s responses. Use a 60s timeout.

## GET /v1/trustpilot/business-search — 1 credit (standard)

Search Trustpilot businesses

- `query` (required) — Business name or keyword (e.g. 'nike'). Matches companies, not products; do not pass a bare domain.
- `depth` (optional, integer) — Number of business results to retrieve (default 20, multiples of 10, max 140). More results = longer task time.

```bash
curl "https://www.socialcrawl.dev/v1/trustpilot/business-search?query=nike" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/trustpilot/reviews — 5 credits (advanced)

Get Trustpilot reviews for a business

- `domain` (required) — The business's domain on Trustpilot (e.g. 'www.nike.com' or 'booking.com'), from business-search.
- `depth` (optional, integer) — Number of reviews to retrieve (default 20, multiples of 20, max 200). There is no pagination beyond 200.
- `sort` (optional, enum: recency | relevance) — Review ordering: `recency` (newest first, default) or `relevance`.

```bash
curl "https://www.socialcrawl.dev/v1/trustpilot/reviews?domain=www.nike.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
