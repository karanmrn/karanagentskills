# Spotify

6 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 6 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/spotify/artist — 1 credit (standard)

Get a Spotify artist

- `id` (optional, string) — Spotify artist ID.
- `url` (optional, string) — Spotify artist URL.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/spotify/artist" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/spotify/track — 1 credit (standard)

Get a Spotify track

- `id` (optional, string) — Spotify track ID.
- `url` (optional, string) — Spotify track URL.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/spotify/track" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/spotify/album — 1 credit (standard)

Get a Spotify album

- `id` (optional, string) — Spotify album ID.
- `url` (optional, string) — Spotify album URL.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/spotify/album" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/spotify/search — 1 credit (standard)

Search Spotify

- `query` (required) — Search query.

```bash
curl "https://www.socialcrawl.dev/v1/spotify/search?query=my first million" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/spotify/podcast — 1 credit (standard)

Get a Spotify podcast

- `id` (optional, string) — Spotify podcast (show) ID.
- `url` (optional, string) — Spotify podcast (show) URL.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/spotify/podcast" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/spotify/podcast/episodes — 1 credit (standard)

List a Spotify podcast's episodes

- `id` (optional, string) — Spotify podcast (show) ID.
- `url` (optional, string) — Spotify podcast (show) URL.
- `cursor` (optional, integer) — Cursor returned by the previous response. Omit for page 1.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/spotify/podcast/episodes" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
