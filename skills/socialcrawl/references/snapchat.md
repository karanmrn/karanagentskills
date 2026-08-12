# Snapchat

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/snapchat/profile — 1 credit (standard)

Get Snapchat user profile

- `handle` (required) — Snapchat username

```bash
curl "https://www.socialcrawl.dev/v1/snapchat/profile?handle=djkhaled305" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
