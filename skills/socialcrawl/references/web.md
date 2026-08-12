# Web

22 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 22 custom (flat/metered) — the exact cost is in each endpoint heading below.

Web endpoints scrape, search, crawl, and map arbitrary web pages — the general-purpose surface for any URL that isn't a first-class social/commerce platform. Crawl/map jobs fan out across a site and can run longer than a single-page fetch.

## GET /v1/web/scrape — 1 credit (custom)

Scrape a web page

- `url` (required) — Public URL to fetch.
- `formats` (optional, string) — Comma-separated output formats such as markdown,screenshot.
- `only_main_content` (optional, boolean)
- `wait_for` (optional, integer)
- `mobile` (optional, boolean)
- `timeout` (optional, integer)
- `max_age` (optional, integer)
- `location_country` (optional, string)
- `screenshot_full_page` (optional, boolean)
- `include_tags` (optional, string)
- `exclude_tags` (optional, string)
- `proxy` (optional, enum: basic | auto | enhanced) — Proxy tier: basic, auto, or enhanced.
- `pdf_parse` (optional, boolean)
- `block_ads` (optional, boolean)
- `remove_base64_images` (optional, boolean)

```bash
curl "https://www.socialcrawl.dev/v1/web/scrape?url=https://example.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/search — 2 credits (custom)

Search the web

- `query` (required) — Search query.
- `sources` (optional, string) — Comma-separated sources: web,news,images.
- `categories` (optional, string)
- `limit` (optional, integer) — Results per source, from 1 to 100.
- `country` (optional, string)
- `location` (optional, string)
- `time_range` (optional, string)
- `sort_by_date` (optional, boolean)
- `include_domains` (optional, string)
- `exclude_domains` (optional, string)
- `include_content` (optional, boolean)

```bash
curl "https://www.socialcrawl.dev/v1/web/search?query=social media data api" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/map — 1 credit (custom)

Map URLs on a site

- `url` (required) — Site URL to map.
- `search` (optional, string) — Optional path or keyword filter.
- `limit` (optional, integer) — Maximum URLs to return, up to 5000.
- `sitemap` (optional, enum: include | skip | only)
- `include_subdomains` (optional, boolean)
- `ignore_query_parameters` (optional, boolean)
- `fresh` (optional, boolean)

```bash
curl "https://www.socialcrawl.dev/v1/web/map?url=https://example.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/extract — 5 credits (custom)

Extract structured data from a web page

- `url` (required) — Public URL to extract from.
- `schema` (optional, string) — JSON object schema describing the data to return.
- `prompt` (optional, string) — Plain-language extraction instruction.
- `only_main_content` (optional, boolean)
- `timeout` (optional, integer)
- `max_age` (optional, integer)
- `proxy` (optional, enum: basic | auto | enhanced)

**At least one of `schema` / `prompt` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/web/extract?url=https://example.com/pricing" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/crawl — 1 credit (custom)

Start an async web crawl

- `url` (required) — Root URL to crawl.
- `limit` (optional, integer) — Maximum pages to crawl.
- `max_depth` (optional, integer)
- `allow_backward_links` (optional, boolean)
- `allow_external_links` (optional, boolean)
- `include_paths` (optional, string)
- `exclude_paths` (optional, string)
- `webhook_url` (optional, string) — Optional webhook URL for terminal job updates.
- `formats` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/web/crawl?url=https://example.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/batch-scrape — 1 credit (custom)

Start an async batch scrape

- `urls` (required) — Array or comma-separated list of public URLs to scrape.
- `ignore_invalid_urls` (optional, boolean) — Skip invalid URLs instead of failing the job.
- `formats` (optional, string)
- `only_main_content` (optional, boolean)
- `proxy` (optional, enum: basic | auto | enhanced)
- `webhook_url` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/web/batch-scrape?urls=https://example.com/a,https://example.com/b" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/jobs — 0 credits (custom)

List async web jobs

- `limit` (optional, integer) — Page size, capped at 100.
- `cursor` (optional, string) — Previous response cursor.

```bash
curl "https://www.socialcrawl.dev/v1/web/jobs" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/jobs/{job_id} — 0 credits (custom)

Get an async web job

- `job_id` (required) — Job id (job_...) returned by POST /v1/web/crawl, POST /v1/web/batch-scrape, or POST /v1/web/agent as data.job_id.

```bash
curl "https://www.socialcrawl.dev/v1/web/jobs/{job_id}?job_id=job_9f3k2n8d1" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/jobs/{job_id} — 0 credits (custom)

Cancel an async web job

- `job_id` (required) — Job id (job_...) returned by POST /v1/web/crawl, POST /v1/web/batch-scrape, or POST /v1/web/agent as data.job_id.

```bash
curl "https://www.socialcrawl.dev/v1/web/jobs/{job_id}?job_id=job_9f3k2n8d1" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/agent — 25 credits (custom)

Start an async web agent job

- `url` (required) — Starting URL folded into the agent instruction.
- `prompt` (required) — Task instruction.
- `model` (optional, enum: spark-1-mini | spark-1-pro) — Firecrawl Spark model: spark-1-mini or spark-1-pro.

```bash
curl "https://www.socialcrawl.dev/v1/web/agent?url=https://example.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/monitors — 0 credits (custom)

Create a web monitor

- `url` (required) — URL or root target to monitor.
- `name` (optional, string) — Human-readable monitor name.
- `mode` (optional, enum: scrape | search) — Monitor target type.
- `cadence_minutes` (optional, integer) — Check interval in minutes: 5-60, or a whole number of hours up to 1440 (120, 180, ...). Hour cadences are scheduled as cron.
- `schedule_text` (optional, string) — Plain-language schedule, such as every 15 minutes.
- `schedule_cron` (optional, string) — Cron schedule. Mutually exclusive with schedule_text.
- `timezone` (optional, string) — IANA timezone for the schedule.
- `webhook_url` (optional, string)
- `query` (optional, string)
- `goal` (optional, string)
- `retention_days` (optional, integer)
- `judge_enabled` (optional, boolean)

```bash
curl "https://www.socialcrawl.dev/v1/web/monitors?url=https://example.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/monitors — 0 credits (custom)

List web monitors

- `cursor` (optional, string) — Pagination cursor.
- `limit` (optional, integer) — Page size.

```bash
curl "https://www.socialcrawl.dev/v1/web/monitors" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/monitors/{monitor_id} — 0 credits (custom)

Get a web monitor

- `monitor_id` (required) — Monitor id (wm_...) returned by POST /v1/web/monitors as data.monitor_id.

```bash
curl "https://www.socialcrawl.dev/v1/web/monitors/{monitor_id}?monitor_id=wm_5d1p8s3k7" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/monitors/{monitor_id} — 0 credits (custom)

Update a web monitor

- `monitor_id` (required) — Monitor id (wm_...) returned by POST /v1/web/monitors as data.monitor_id.
- `status` (optional, enum: active | paused)
- `cadence_minutes` (optional, integer)
- `schedule_text` (optional, string)
- `schedule_cron` (optional, string)
- `timezone` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/web/monitors/{monitor_id}?monitor_id=wm_5d1p8s3k7" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/monitors/{monitor_id} — 0 credits (custom)

Delete a web monitor

- `monitor_id` (required) — Monitor id (wm_...) returned by POST /v1/web/monitors as data.monitor_id.

```bash
curl "https://www.socialcrawl.dev/v1/web/monitors/{monitor_id}?monitor_id=wm_5d1p8s3k7" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/monitors/{monitor_id}/checks — 0 credits (custom)

List web monitor checks

- `monitor_id` (required) — Monitor id (wm_...) returned by POST /v1/web/monitors as data.monitor_id.
- `limit` (optional, integer)

```bash
curl "https://www.socialcrawl.dev/v1/web/monitors/{monitor_id}/checks?monitor_id=wm_5d1p8s3k7" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/sessions — 5 credits (custom)

Create an interactive web session

- `url` (required) — URL to open in the session after creation.
- `ttl_seconds` (optional, integer) — Session TTL in seconds.
- `activity_ttl_seconds` (optional, integer)
- `stream_web_view` (optional, boolean)

```bash
curl "https://www.socialcrawl.dev/v1/web/sessions?url=https://example.com" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/sessions — 0 credits (custom)

List interactive web sessions

- `limit` (optional, integer) — Page size.

```bash
curl "https://www.socialcrawl.dev/v1/web/sessions" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/sessions/{session_id} — 0 credits (custom)

Get an interactive web session

- `session_id` (required) — Session id (ws_...) returned by POST /v1/web/sessions as data.session_id.

```bash
curl "https://www.socialcrawl.dev/v1/web/sessions/{session_id}?session_id=ws_3g7x1v5m2" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/sessions/{session_id}/execute — 0 credits (custom)

Execute an interaction in a web session

- `session_id` (required) — SocialCrawl session id.
- `code` (required) — Code to execute in the browser sandbox.
- `language` (optional, enum: node | python | bash) — Execution language: node, python, or bash.
- `timeout` (optional, integer) — Execution timeout in seconds.

```bash
curl "https://www.socialcrawl.dev/v1/web/sessions/{session_id}/execute?session_id=ws_3g7x1v5m2" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/sessions/{session_id} — 0 credits (custom)

Close an interactive web session

- `session_id` (required) — Session id (ws_...) returned by POST /v1/web/sessions as data.session_id.

```bash
curl "https://www.socialcrawl.dev/v1/web/sessions/{session_id}?session_id=ws_3g7x1v5m2" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/web/parse — 1 credit (custom)

Parse an uploaded document

- `file` (required) — Multipart file field.
- `filename` (optional, string)
- `mime_type` (optional, string) — Optional MIME type override.
- `url` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/web/parse?file=document.pdf" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
