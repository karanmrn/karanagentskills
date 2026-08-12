# Utility

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 premium (10) — the exact cost is in each endpoint heading below.

## GET /v1/utility/age-gender — 10 credits (premium)

Detect age and gender

- `url` (required) — Social profile URL whose avatar should be analyzed (e.g. a Twitter/X profile URL)

```bash
curl "https://www.socialcrawl.dev/v1/utility/age-gender?url=https://twitter.com/levelsio" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
