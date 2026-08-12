# Universal Search

2 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 2 custom (flat/metered) — the exact cost is in each endpoint heading below.

Universal search fans out one query across many sources in parallel, then fuses, reranks, enriches with top comments, and clusters the results. `/v1/search/everywhere` supports two response modes via the `Accept` header: `application/json` (default, full ranked set) or `text/event-stream` (typed SSE chunks: `meta`, `source_started`, `items`, `source_failed`, `ranked_partial`, `ranked_final`, `comments_enriched`, `clusters`, `done`, `error`). Fully refunded when every source fails or returns empty. Prefer this over fanning out per-platform yourself when the user wants one query across many platforms.

## GET /v1/search/everywhere — 20 credits (custom)

Universal social search across 12 platforms

- `query` (required) — Search query (1–512 chars)
- `lookback_days` (optional, integer) — Days to look back (1–365+, default 30); mutually exclusive with from_date/to_date.
- `from_date` (optional, string) — ISO YYYY-MM-DD lower bound; mutually exclusive with lookback_days.
- `to_date` (optional, string) — ISO YYYY-MM-DD upper bound; defaults to today when from_date is set alone.
- `sources` (optional, string) — Optional CSV allowlist of source names (mutually exclusive with exclude).
- `exclude` (optional, string) — Optional CSV blocklist of source names (mutually exclusive with sources).

```bash
curl "https://www.socialcrawl.dev/v1/search/everywhere?query=kanye west" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/search/forums — 10 credits (custom)

Fused forum search across Reddit, Hacker News, and Naver 지식iN/카페 — with top comments inline on hero threads by default.

- `query` (required) — Search query (2–256 chars), forwarded to every forum search.
- `sources` (optional, string) — Optional CSV allowlist of forum sources (reddit, hackernews, naver_kin, naver_cafe). Mutually exclusive with exclude.
- `exclude` (optional, string) — Optional CSV blocklist of forum sources. Mutually exclusive with sources.
- `comments` (optional, string) — Comment enrichment toggle (on|off, default on). 'off' returns thread-only.
- `timeframe` (optional, string) — Recency window passed to Reddit; HN filtered client-side (all|day|week|month|year, default all).
- `lookback_days` (optional, integer) — Alt recency window in days (1–365); HN filtered client-side.

```bash
curl "https://www.socialcrawl.dev/v1/search/forums?query=airpods pro 3 battery" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
