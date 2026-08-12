# Pinterest

5 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 5 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/pinterest/search — 1 credit (standard)

Search Pinterest pins

- `query` (required) — Search query
- `cursor` (optional, string) — Cursor
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/pinterest/search?query=home decor ideas" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/pinterest/pin — 1 credit (standard)

Get Pinterest pin details

- `url` (required) — Full URL of the Pinterest pin
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/pinterest/pin?url=https://www.pinterest.com/pin/1234567890/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/pinterest/url-stats — 1 credit (standard)

Get Pinterest save counts for external URLs

- `urls` (required) — Comma-separated list of 1–10 absolute http(s):// URLs, passed to Pinterest verbatim. Variants (https vs http, with/without trailing slash, with/without query string) are counted as different URLs.

```bash
curl "https://www.socialcrawl.dev/v1/pinterest/url-stats?urls=https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/pinterest/board — 1 credit (standard)

Get Pinterest board

- `url` (required) — Full URL of the Pinterest board
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/pinterest/board?url=https://www.pinterest.com/lizmrodgers/moms-night/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/pinterest/user/boards — 1 credit (standard)

List Pinterest user boards

- `handle` (required) — The username of the user to get boards for. (e.g. broadstbullycom from https://www.pinterest.com/broadstbullycom/)
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/pinterest/user/boards?handle=pinterest" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
