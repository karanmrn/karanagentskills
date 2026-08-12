# Google Trends

2 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 2 advanced (5) — the exact cost is in each endpoint heading below.

## GET /v1/google_trends/explore — 5 credits (advanced)

Get Google Trends interest over time

- `keywords` (required) — 1-5 comma-separated keywords (e.g. 'reverse audio,voice changer'). With multiple keywords the 0-100 values are normalised across the set for direct comparison.
- `location` (optional, string) — Location as a DFS name ('United States') or numeric code ('2840'). Defaults to worldwide-leaning US.
- `timeframe` (optional, enum: past_hour | past_4_hours | past_day | past_7_days | past_30_days | past_90_days | past_12_months | past_5_years) — Preset time window: past_hour, past_4_hours, past_day, past_7_days, past_30_days, past_90_days, past_12_months, or past_5_years. Defaults to past_12_months.
- `category` (optional, integer) — Numeric Google Trends category code to scope the query (default 0 = all categories).

```bash
curl "https://www.socialcrawl.dev/v1/google_trends/explore?keywords=uv index" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_trends/rising — 5 credits (advanced)

Get related + rising Google Trends queries

- `keyword` (required) — Single keyword to expand (e.g. 'uv index'). Google Trends returns the related-queries list for one keyword only.
- `location` (optional, string) — Location as a DFS name ('United States') or numeric code ('2840'). Defaults to worldwide-leaning US.
- `timeframe` (optional, enum: past_hour | past_4_hours | past_day | past_7_days | past_30_days | past_90_days | past_12_months | past_5_years) — Preset time window: past_hour, past_4_hours, past_day, past_7_days, past_30_days, past_90_days, past_12_months, or past_5_years. Defaults to past_12_months.

```bash
curl "https://www.socialcrawl.dev/v1/google_trends/rising?keyword=uv index" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
