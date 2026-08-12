# Polymarket

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 advanced (5) — the exact cost is in each endpoint heading below.

## GET /v1/polymarket/research — 5 credits (advanced)

Polymarket prediction markets — multi-query research

- `query` (required) — The research topic — free-text natural language (e.g. 'last 30 days bitcoin halving', 'kanye west tour'). Framing prefixes like 'last N days' and 'what are people saying about' are stripped automatically before expansion.
- `limit` (optional, integer) — Max results per result type on each fan-out call (events / markets / profiles). Bounds the response size. Defaults to 10.

```bash
curl "https://www.socialcrawl.dev/v1/polymarket/research?query=trump 2028 election" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
