# Tripadvisor

2 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 2 standard (1 credit) — the exact cost is in each endpoint heading below.

**Latency:** Tripadvisor endpoints are task-polled upstream — expect ~10–45s responses. Use a 60s timeout.

**Two-step:** `reviews` needs the `url_path` returned by `search` first.

## GET /v1/tripadvisor/search — 1 credit (standard)

Search TripAdvisor businesses & places

- `q` (required) — Business category, company name, or prominent place (e.g. 'pizza restaurant').
- `location` (optional, string) — Full location name (e.g. 'New York,New York,United States'). Default: United States. Results are location-bound.
- `language` (optional, string) — Optional language code to narrow results, e.g. 'en'.
- `depth` (optional, integer) — Number of results to retrieve (multiples of 30, default 30, max 60 on this synchronous endpoint).

```bash
curl "https://www.socialcrawl.dev/v1/tripadvisor/search?q=pizza restaurant" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tripadvisor/reviews — 1 credit (standard)

Get TripAdvisor reviews for a place

- `url_path` (required) — The TripAdvisor `url_path` of the place (from a search result), e.g. 'Hotel_Review-g60763-d23462501-Reviews-Margaritaville_Times_Square-New_York_City_New_York.html'.
- `depth` (optional, integer) — Number of reviews to retrieve (multiples of 10, default 10, max 30 on this synchronous endpoint).
- `sort_by` (optional, enum: most_recent | detailed_reviews) — Review ordering: `most_recent` or `detailed_reviews`.
- `rating` (optional, enum: excellent | very_good | average | poor | terrible) — Filter by traveler rating bucket: excellent | very_good | average | poor | terrible.
- `visit_type` (optional, enum: families | couples | solo | business | friends) — Filter by traveler type: families | couples | solo | business | friends.
- `search_reviews_keyword` (optional, string) — Only return reviews containing this keyword.
- `translate` (optional, boolean) — Translate reviews to the place's domain language (default true). The `translated` flag + `original_language` are always returned.

```bash
curl "https://www.socialcrawl.dev/v1/tripadvisor/reviews?url_path=Hotel_Review-g60763-d23462501-Reviews-Margaritaville_Times_Square-New_York_City_New_York.html" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
