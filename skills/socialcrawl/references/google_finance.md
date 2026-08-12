# Google Finance

3 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 2 standard (1 credit), 1 advanced (5) — the exact cost is in each endpoint heading below.

## GET /v1/google_finance/quote — 5 credits (advanced)

Get a financial instrument quote

- `keyword` (required) — Instrument identifier: TICKER:EXCHANGE for stocks/ETFs/indices ('GOOGL:NASDAQ', '.INX:INDEXSP') or a forex/crypto pair ('EUR-USD', 'BTC-USD'). Use the `id` returned by ticker-search.
- `language` (optional, string) — Language as a DFS name ('English') or 2-letter code ('en'). Defaults to English.
- `location` (optional, string) — Location as a DFS name ('United States') or numeric code ('2840'). Defaults to the US.

```bash
curl "https://www.socialcrawl.dev/v1/google_finance/quote?keyword=GOOGL:NASDAQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_finance/ticker-search — 1 credit (standard)

Search financial instruments by name

- `keyword` (required) — Company / instrument name to search for (e.g. 'Apple', 'Euro', 'Bitcoin').
- `category` (optional, enum: all | stock | index | mutual_fund | currency | futures) — Restrict to one instrument class: all (default), stock, index, mutual_fund, currency, or futures. A class with no matches returns an empty list.
- `language` (optional, string) — Language as a DFS name ('English') or 2-letter code ('en'). Defaults to English.
- `location` (optional, string) — Location as a DFS name ('United States') or numeric code ('2840'). Defaults to the US.

```bash
curl "https://www.socialcrawl.dev/v1/google_finance/ticker-search?keyword=Apple" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_finance/markets — 1 credit (standard)

Get a markets overview (indices + movers)

- `language` (optional, string) — Language as a DFS name ('English') or 2-letter code ('en'). Defaults to English.
- `location` (optional, string) — Location as a DFS name ('United States') or numeric code ('2840'). Defaults to the US.

```bash
curl "https://www.socialcrawl.dev/v1/google_finance/markets" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
