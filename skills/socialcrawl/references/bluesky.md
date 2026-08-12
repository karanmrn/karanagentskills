# Bluesky

3 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 3 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/bluesky/profile — 1 credit (standard)

Get a Bluesky profile

- `handle` (required) — Bluesky handle (e.g. `espn.com`).

```bash
curl "https://www.socialcrawl.dev/v1/bluesky/profile?handle=espn.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/bluesky/user/posts — 1 credit (standard)

List a Bluesky user's posts

- `handle` (optional, string) — Bluesky handle.
- `user_id` (optional, string) — Bluesky `did` (Bluesky's internal user ID format, e.g. `did:plc:x7d6j54pm22ufehkes6jo4jf`).

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/bluesky/user/posts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/bluesky/post — 1 credit (standard)

Get a Bluesky post

- `url` (required) — Bluesky post URL.

```bash
curl "https://www.socialcrawl.dev/v1/bluesky/post?url=https://bsky.app/profile/espn.com/post/3lqdfq7fkvm2g" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
