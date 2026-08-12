# Content Analysis

10 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit), 6 custom (flat/metered) — the exact cost is in each endpoint heading below.

Content Analysis endpoints surface brand mentions and per-mention sentiment across the open web. Results are passthrough (native upstream keys), not the unified Author/Post schema.

## GET /v1/content_analysis/search — 20 credits (custom)

Search web citations of a keyword with per-mention sentiment

- `keyword` (required) — Brand or term to find mentions of. Wrap in escaped double-quotes for an exact phrase (e.g. "logitech mouse").
- `page_type` (optional, enum: ecommerce | news | blogs | message-boards | organization) — Narrow to one or more page types (comma-separated): ecommerce, news, blogs, message-boards, organization. Translated to a page_types filter upstream.
- `search_mode` (optional, enum: as_is | one_per_domain) — as_is (default) returns every matching page; one_per_domain dedupes to the top page per domain.
- `limit` (optional, integer) — Number of citations to return per page (1–100, default 10). Paginate via `cursor` for more.
- `cursor` (optional, string) — Opaque pagination cursor — pass the `next_cursor` from the previous response to fetch the next page.
- `order_by` (optional, string) — Sort rules as "field,direction"; separate multiple rules with ";" (e.g. content_info.sentiment_connotations.anger,desc).
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array (≤8 conditions). Combined with page_type via AND when both are present.

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/search?keyword=openai" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/summary — 20 credits (custom)

Aggregate mention summary for a keyword

- `keyword` (required) — Brand or term to summarize.
- `page_type` (optional, enum: ecommerce | news | blogs | message-boards | organization) — Narrow to one or more page types (comma-separated): ecommerce, news, blogs, message-boards, organization.
- `positive_connotation_threshold` (optional, string) — Minimum positive-connotation probability (0–1, default 0.4) for a mention to count as positive.
- `sentiments_connotation_threshold` (optional, string) — Minimum sentiment-connotation probability (0–1, default 0.4) for the 6-axis emotion buckets.
- `internal_list_limit` (optional, integer) — Cap on internal arrays such as top_domains / categories (1–20).
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array (≤8 conditions).

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/summary?keyword=openai" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/sentiment — 20 credits (custom)

Sentiment breakdown for a keyword

- `keyword` (required) — Brand or term to analyze.
- `page_type` (optional, enum: ecommerce | news | blogs | message-boards | organization) — Narrow to one or more page types (comma-separated): ecommerce, news, blogs, message-boards, organization.
- `positive_connotation_threshold` (optional, string) — Minimum positive-connotation probability (0–1, default 0.4).
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array (≤8 conditions).

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/sentiment?keyword=openai" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/rating-distribution — 20 credits (custom)

Rating histogram for a keyword

- `keyword` (required) — Product or term to build the rating histogram for.
- `page_type` (optional, enum: ecommerce | news | blogs | message-boards | organization) — Narrow to one or more page types (comma-separated): ecommerce, news, blogs, message-boards, organization.
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array (≤8 conditions).

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/rating-distribution?keyword=iphone" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/phrase-trends — 20 credits (custom)

Keyword mention volume + sentiment over time

- `keyword` (required) — Brand or term to trend.
- `date_from` (required) — Start of the date range (yyyy-mm-dd).
- `date_to` (optional, string) — End of the date range (yyyy-mm-dd); defaults to today.
- `date_group` (optional, enum: day | week | month) — Bucket size: day, week, or month (default month).
- `page_type` (optional, enum: ecommerce | news | blogs | message-boards | organization) — Narrow to one or more page types (comma-separated): ecommerce, news, blogs, message-boards, organization.
- `internal_list_limit` (optional, integer) — Cap on internal arrays per bucket (1–20).
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array (≤8 conditions).

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/phrase-trends?keyword=openai" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/category-trends — 20 credits (custom)

Category mention volume + sentiment over time

- `category_code` (required) — Numeric category code from the /content_analysis/categories taxonomy (e.g. 10021 = Apparel).
- `date_from` (required) — Start of the date range (yyyy-mm-dd).
- `date_to` (optional, string) — End of the date range (yyyy-mm-dd); defaults to today.
- `date_group` (optional, enum: day | week | month) — Bucket size: day, week, or month (default month).
- `internal_list_limit` (optional, integer) — Cap on internal arrays per bucket (1–20).
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array (≤8 conditions).

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/category-trends?category_code=10021" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/languages — 1 credit (standard)

List supported Content Analysis languages

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/languages" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/locations — 1 credit (standard)

List supported Content Analysis locations

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/locations" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/categories — 1 credit (standard)

List the Content Analysis category taxonomy

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/categories" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/content_analysis/filters — 1 credit (standard)

List the filterable fields for Content Analysis

```bash
curl "https://www.socialcrawl.dev/v1/content_analysis/filters" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
