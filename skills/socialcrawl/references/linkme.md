# Linkme

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/linkme/page — 1 credit (standard)

Get Linkme profile

- `url` (required) — Full URL of the Linkme page

```bash
curl "https://www.socialcrawl.dev/v1/linkme/page?url=https://link.me/example" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
