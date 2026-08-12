# Linktree

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/linktree/page — 1 credit (standard)

Get Linktree page

- `url` (required) — Full URL of the Linktree page

```bash
curl "https://www.socialcrawl.dev/v1/linktree/page?url=https://linktr.ee/charlidamelio" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
