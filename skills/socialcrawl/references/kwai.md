# Kwai

3 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 3 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/kwai/profile — 1 credit (standard)

Get a Kwai user profile

- `handle` (optional, string) — Kwai profile handle (without the @)
- `url` (optional, string) — Kwai profile URL

**At least one of `handle` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/kwai/profile" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/kwai/user/posts — 1 credit (standard)

List a Kwai user's posts

- `handle` (optional, string) — Kwai profile handle (without the @)
- `url` (optional, string) — Kwai profile URL
- `cursor` (optional, string) — Cursor from the previous response for the next page
- `count` (optional, integer) — Number of posts to return (max 50)

**At least one of `handle` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/kwai/user/posts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/kwai/post — 1 credit (standard)

Get a Kwai post

- `url` (optional, string) — Full URL of the Kwai post

```bash
curl "https://www.socialcrawl.dev/v1/kwai/post" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
