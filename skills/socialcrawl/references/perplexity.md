# Perplexity

1 endpoint. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/perplexity/research — 1 credit (standard)

Web research via Perplexity Sonar

- `query` (required) — Natural-language research prompt. Sonar autonomously searches the live web and grounds the response in real sources. No prompt-engineering required — phrase it as you would to a search engine or research assistant.

```bash
curl "https://www.socialcrawl.dev/v1/perplexity/research?query=What is the capital of France?" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
