# Kick

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/kick/clip — 1 credit (standard)

Get Kick clip details

- `url` (required) — Full URL of the Kick clip

```bash
curl "https://www.socialcrawl.dev/v1/kick/clip?url=https://kick.com/xqc/clips/clip_abc123" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
