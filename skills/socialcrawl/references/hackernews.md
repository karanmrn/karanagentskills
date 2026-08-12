# Hacker News

4 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/hackernews/search — 1 credit (standard)

Search Hacker News

- `query` (required) — Free-text search term.
- `tags` (optional, string) — Algolia tag filter — comma-separated. Common values: "story", "comment", "poll", "show_hn", "ask_hn", "front_page", "author_<username>". Defaults to "story".
- `numericFilters` (optional, string) — Algolia numeric filter expression on `created_at_i` (the only filterable numeric attribute) — e.g. "created_at_i>1700000000". Combine with commas for AND. No filter is applied by default.
- `hitsPerPage` (optional, integer) — Hits per page (1–1000). Defaults to 30.
- `page` (optional, integer) — 0-indexed page number for pagination.

```bash
curl "https://www.socialcrawl.dev/v1/hackernews/search?query=claude code" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/hackernews/story — 1 credit (standard)

Get a Hacker News story

- `id` (required) — HN story id (the numeric `objectID`).

```bash
curl "https://www.socialcrawl.dev/v1/hackernews/story?id=8863" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/hackernews/story/comments — 1 credit (standard)

Get comments on a Hacker News story

- `id` (required) — HN story id (the numeric `objectID`).

```bash
curl "https://www.socialcrawl.dev/v1/hackernews/story/comments?id=8863" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/hackernews/profile — 1 credit (standard)

Get a Hacker News user profile

- `handle` (required) — Hacker News username (case-sensitive, e.g. `pg` or `kogir`).

```bash
curl "https://www.socialcrawl.dev/v1/hackernews/profile?handle=pg" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
