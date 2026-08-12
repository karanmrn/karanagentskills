# Rumble

5 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit), 1 premium (10) — the exact cost is in each endpoint heading below.

## GET /v1/rumble/search — 1 credit (standard)

Search Rumble videos

- `query` (required) — Search query.
- `cursor` (optional, string) — Cursor from the previous response — the next page number (e.g. `2`).

```bash
curl "https://www.socialcrawl.dev/v1/rumble/search?query=funny cats" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/rumble/channel/videos — 1 credit (standard)

List videos for a Rumble channel

- `handle` (optional, string) — Rumble channel handle.
- `url` (optional, string) — Rumble channel URL.
- `cursor` (optional, string) — Cursor from the previous response — the next page number (e.g. `2`).

**At least one of `handle` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/rumble/channel/videos" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/rumble/video — 1 credit (standard)

Get a Rumble video

- `url` (required) — Rumble video URL.

```bash
curl "https://www.socialcrawl.dev/v1/rumble/video?url=https://rumble.com/v79xhhm-discovery-example.html" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/rumble/video/transcript — 10 credits (premium)

Get a Rumble video transcript

- `url` (required) — Rumble video URL.

```bash
curl "https://www.socialcrawl.dev/v1/rumble/video/transcript?url=https://rumble.com/v784xoi-president-donald-j.-trump-and-secwar-pete-hegseth-hold-a-press-conference-a.html" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/rumble/video/comments — 1 credit (standard)

List top-level comments on a Rumble video

- `url` (required) — Rumble video URL.

```bash
curl "https://www.socialcrawl.dev/v1/rumble/video/comments?url=https://rumble.com/v792vns-example.html" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
