# Tavily

4 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/tavily/search — 1 credit (standard)

Tavily web search with optional LLM-generated answer

- `query` (required) — The search query — natural-language free text.
- `search_depth` (optional, enum: basic | advanced | fast | ultra-fast) — Latency-vs-relevance tradeoff. `basic` is the default; `advanced` unlocks `chunks_per_source` and higher-relevance ranking.
- `topic` (optional, enum: general | news | finance) — Search category. Defaults to `general`. Use `news` for time-sensitive queries and `finance` for market data.
- `time_range` (optional, enum: day | week | month | year | d | w | m | y) — Time window relative to now. Accepts `day` / `week` / `month` / `year` (or shorthand `d` / `w` / `m` / `y`).
- `max_results` (optional, integer) — Number of results to return (1–20). Defaults to 5.
- `chunks_per_source` (optional, integer) — Max relevant chunks returned per source (1–5). Only honoured when `search_depth=advanced`. Defaults to 3.
- `include_images` (optional, boolean) — Include images alongside the result content.
- `include_image_descriptions` (optional, boolean) — Include AI-generated descriptions for the returned images.
- `include_answer` (optional, boolean) — Include an LLM-generated answer string synthesised from the top sources.
- `include_raw_content` (optional, boolean) — Include the raw HTML/text alongside the cleaned content.
- `include_domains` (optional, string) — Comma-separated list of domains to restrict results to (e.g. `nytimes.com,reuters.com`).
- `exclude_domains` (optional, string) — Comma-separated list of domains to exclude from results.
- `country` (optional, string) — ISO 3166-1 alpha-2 country code to bias results toward.
- `start_date` (optional, string) — Inclusive lower bound on result publish date (YYYY-MM-DD).
- `end_date` (optional, string) — Inclusive upper bound on result publish date (YYYY-MM-DD).

```bash
curl "https://www.socialcrawl.dev/v1/tavily/search?query=claude opus 4.7 release notes" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tavily/extract — 1 credit (standard)

Extract clean content from one or more URLs

- `urls` (required) — Comma-separated list of URLs to extract (max 20).
- `extract_depth` (optional, enum: basic | advanced) — Extraction strategy. `basic` is the default and faster; `advanced` handles harder pages but takes longer.
- `format` (optional, enum: markdown | text) — Output format for the extracted content. `markdown` (default) preserves structure; `text` is plain.
- `include_images` (optional, boolean) — Include images extracted from each URL.
- `include_favicon` (optional, boolean) — Include the favicon URL for each page.
- `timeout` (optional, integer) — Per-URL timeout in seconds (1–60).

```bash
curl "https://www.socialcrawl.dev/v1/tavily/extract?urls=https://en.wikipedia.org/wiki/Lionel_Messi" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tavily/map — 1 credit (standard)

Map a website's sitegraph

- `url` (required) — Root URL to begin mapping.
- `max_depth` (optional, integer) — Maximum link depth from the root URL. Defaults to 1.
- `max_breadth` (optional, integer) — Maximum number of links followed per level (per page). Defaults to 20.
- `limit` (optional, integer) — Total number of links the mapper will process before stopping. Defaults to 50.
- `instructions` (optional, string) — Natural-language instructions for the mapper (e.g. 'Find all pages related to API documentation').
- `select_paths` (optional, string) — Comma-separated regex patterns — only include URLs whose path matches.
- `select_domains` (optional, string) — Comma-separated regex patterns — only include URLs whose domain matches.
- `exclude_paths` (optional, string) — Comma-separated regex patterns — exclude URLs whose path matches.
- `exclude_domains` (optional, string) — Comma-separated regex patterns — exclude URLs whose domain matches.
- `allow_external` (optional, boolean) — Whether to follow / return links to external domains. Defaults to true.
- `timeout` (optional, integer) — Maximum time in seconds (10–150).
- `categories` (optional, string) — Comma-separated list of category hints to bias mapping toward.

```bash
curl "https://www.socialcrawl.dev/v1/tavily/map?url=https://docs.tavily.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tavily/crawl — 1 credit (standard)

Crawl a website with LLM-driven path selection

- `url` (required) — Root URL to begin crawling.
- `max_depth` (optional, integer) — Maximum link depth from the root URL. Defaults to 1.
- `max_breadth` (optional, integer) — Maximum number of links followed per level (per page). Defaults to 20.
- `limit` (optional, integer) — Total number of pages the crawler will process before stopping. Defaults to 50.
- `instructions` (optional, string) — Natural-language instructions for the crawler (e.g. 'Find all product pages with pricing').
- `select_paths` (optional, string) — Comma-separated regex patterns — only crawl URLs whose path matches.
- `select_domains` (optional, string) — Comma-separated regex patterns — only crawl URLs whose domain matches.
- `exclude_paths` (optional, string) — Comma-separated regex patterns — skip URLs whose path matches.
- `exclude_domains` (optional, string) — Comma-separated regex patterns — skip URLs whose domain matches.
- `allow_external` (optional, boolean) — Whether to follow links to external domains. Defaults to true.
- `extract_depth` (optional, enum: basic | advanced) — Per-page extraction strategy. `basic` is faster; `advanced` handles harder pages.
- `format` (optional, enum: markdown | text) — Output format for extracted content. `markdown` (default) or `text`.
- `categories` (optional, string) — Comma-separated list of category hints to bias the crawl toward.

```bash
curl "https://www.socialcrawl.dev/v1/tavily/crawl?url=https://docs.tavily.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
