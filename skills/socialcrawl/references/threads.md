# Threads

5 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 5 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/threads/profile — 1 credit (standard)

Get Threads user profile

- `handle` (required) — Threads username without the @ symbol

```bash
curl "https://www.socialcrawl.dev/v1/threads/profile?handle=zuck" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/threads/user/posts — 1 credit (standard)

List Threads user posts

- `handle` (required) — Threads username without the @ symbol
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/threads/user/posts?handle=zuck" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/threads/post — 1 credit (standard)

Get Threads post details

- `url` (required) — Full URL of the Threads post
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/threads/post?url=https://www.threads.net/@zuck/post/CwABCDEFGHI" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/threads/search — 1 credit (standard)

Search Threads posts

- `query` (required) — Search keyword or phrase to find Threads posts
- `start_date` (optional, string) — Start date to search for
- `end_date` (optional, string) — End date to search for
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/threads/search?query=artificial intelligence" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/threads/search/users — 1 credit (standard)

Search Threads users

- `query` (required) — Search keyword or phrase to find Threads users

```bash
curl "https://www.socialcrawl.dev/v1/threads/search/users?query=tech" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
