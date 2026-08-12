# Pillar

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/pillar/page — 1 credit (standard)

Get Pillar page

- `url` (required) — Full URL of the Pillar page

```bash
curl "https://www.socialcrawl.dev/v1/pillar/page?url=https://pillar.io/example" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
