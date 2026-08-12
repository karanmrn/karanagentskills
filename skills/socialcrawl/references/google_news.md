# Google News

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/google_news/search — 1 credit (standard)

Search Google News

- `keyword` (required) — Search query (e.g. 'openai'). Supports any language; pass the matching language_code. Advanced operators (site:, intitle:, cache:, …) are not supported.
- `depth` (optional, integer) — Number of articles to retrieve (default 10, multiples of 10, max 100). No pagination beyond depth.
- `location_code` (optional, integer) — Google location code (e.g. 2840 = United States). Use one of location_code / location_name / location_coordinate.
- `location_name` (optional, string) — Google location name (e.g. 'South Korea').
- `location_coordinate` (optional, string) — GPS target as 'latitude,longitude,radius_mm' (e.g. '40.7128,-74.0060,200') for local-news radius queries.
- `language_code` (optional, string) — Google language code (e.g. 'en', 'ko'). Default 'en'.
- `time_range` (optional, enum: hour | day | week | month | year) — Only return articles published within this window: hour, day, week, month, or year.

```bash
curl "https://www.socialcrawl.dev/v1/google_news/search?keyword=openai" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
