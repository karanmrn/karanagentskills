# SocialCrawl API Overview

## Base URL

```
https://www.socialcrawl.dev
```

## Authentication

Pass your API key in the `x-api-key` header with every request:

```bash
curl -s -H "x-api-key: $SOCIALCRAWL_API_KEY" \
  "https://www.socialcrawl.dev/v1/tiktok/profile?handle=charlidamelio"
```

## Surface

**44 platforms, 357 active endpoints**. Most are `GET /v1/{platform}/{resource}`. Two surfaces sit on top of the registry: the cross-platform **Prism** composites (`/v1/prism/*` and per-platform `profile/full` / `omni-search`), and the stateful **Monitors** family (`/v1/monitors/*`, which also uses POST/PATCH/DELETE and is not counted in the 357). See [prism.md](prism.md) and [monitors.md](monitors.md).

## Response Format

All successful responses follow this envelope:

```json
{
  "success": true,
  "platform": "tiktok",
  "endpoint": "/v1/tiktok/profile",
  "data": { ... },
  "credits_used": 1,
  "credits_remaining": 4999,
  "request_id": "req-XXXXX",
  "cached": false
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "type": "INSUFFICIENT_CREDITS",
    "message": "Your account has 0 credits remaining. This endpoint requires 1 credits.",
    "status": 402,
    "doc_url": "https://www.socialcrawl.dev/docs/errors/insufficient-credits"
  },
  "credits_remaining": 0,
  "request_id": "req-XXXXX"
}
```

## Response Headers

| Header | Value |
|--------|-------|
| X-Request-Id | Unique request identifier (`req-XXXXX`) |
| X-Credits-Used | Credits consumed by this request (`0` on cache hit, idempotent replay, or refunded error) |
| X-Credits-Remaining | Balance after deduction |
| X-Cache | `HIT` or `MISS` |
| X-Idempotent-Replay | `"true"` when the request was served as an idempotent replay. Absent otherwise. |
| Retry-After | `"30"` (seconds) — only on 503 circuit-breaker responses |
| Allow | `"GET"` — only on 405 `METHOD_NOT_ALLOWED` responses |

## Credit System

| Tier | Cost | Endpoints | Typical endpoints |
|------|------|-----------|-------------------|
| standard | 1 credit | 176 | Profiles, posts, comments, search, Naver corpora, GitHub direct calls, reference data |
| advanced | 5 credits | 90 | Ad libraries, trending, audience analytics, app data, business/place reviews, Google Trends, LinkedIn social graph + jobs, Instagram relationship/discovery data, GitHub composites |
| premium | 10 credits | 18 | Video transcripts, age-gender detection, LinkedIn people/job search + reactions, app listings search |
| **custom (flat / metered)** | **varies (0–50)** | 73 | `/v1/search/everywhere` (20) & `search/forums` (10); `naver/brief` (10); `{platform}/profile/full` (5); web scrape/crawl; all `/v1/prism/*` composites (0–50, flat or metered per recipe) |

Counted by underlying tier (custom endpoints folded into their base tier), the split is **210 standard · 117 advanced · 30 premium = 357**. Per-endpoint costs for every endpoint: see [pricing.md](pricing.md).

Every account starts with **100 free credits**. Credit packs (one-time, no subscription): Starter 2,500 (£15), Growth 20,000 (£49), Pro 150,000 (£299), Enterprise custom — current packs at https://socialcrawl.dev/pricing.

**Auto-refunds.** Credits are refunded automatically on `502 UPSTREAM_ERROR`, `503 SERVICE_UNAVAILABLE`, `500 INTERNAL_ERROR`, and `404 RESOURCE_NOT_FOUND` from the empty-upstream guard. You only pay for calls that return real data.

## Credit Balance

Check remaining credits via the public, API-key-authed meta endpoint (costs **0 credits**, never cached):

```bash
curl -s -H "x-api-key: $SOCIALCRAWL_API_KEY" \
  "https://www.socialcrawl.dev/v1/credits/balance"
```

```json
{
  "success": true,
  "platform": "meta",
  "endpoint": "/v1/credits/balance",
  "data": {
    "balance": 8432,
    "recent_deductions": { "last_24h": 128, "last_7d": 1043 }
  },
  "credits_used": 0,
  "credits_remaining": 8432,
  "request_id": "req-XXXXX",
  "cached": false
}
```

The dashboard UI uses a separate session-authed `/api/credits/balance` route — programmatic callers must use `/v1/credits/balance`.

For a full credit ledger (dispute-grade receipts — deductions negative, refunds positive, newest first), call `GET /v1/credits/transactions` (also **0 credits**, never cached). It is cursor-paginated (`limit` defaults to 50, capped at 100) and filterable by `request_id`:

```bash
curl -s -H "x-api-key: $SOCIALCRAWL_API_KEY" \
  "https://www.socialcrawl.dev/v1/credits/transactions?limit=50"
```

## Unified Canonical Schemas

Author, Post, and Comment endpoints are normalized through per-platform field maps into one canonical shape, validated at the wire — the same JSON structure whether the data came from TikTok, Reddit, or Bluesky.

**Author** (`data.author`): `id`, `username`, `display_name`, `avatar_url`, `bio`, `verified`, `followers`, `following`, `posts_count`, `likes_count`, `url`, `location`, `external_url`. IDs are bare and prefix-stripped (Bluesky `did:`, Spotify `spotify:artist:`, Reddit `t2_` all stripped).

**Post** (`data.post`, or `data.items[].post` in lists): `id`, `url`, `content.{text, media_urls, thumbnail_url, duration_seconds}`, `author.{username, display_name, avatar_url, verified}`, `engagement.{views, likes, comments, shares, saves}`, `flags.{nsfw, spoiler, pinned, deleted}`, `published_at`. `media_urls` is an array for carousels. `flags.deleted` is always present.

**Comment** (`data.comment`, or `data.items[].comment` in lists): `id`, `url`, `parent_id`, `post_id`, `text`, `author.{username, display_name, avatar_url, verified}`, `engagement.{likes, replies}`, `flags.{pinned, deleted}`, `published_at`. Deleted/removed sentinels (`[deleted]`, `[removed]`) never reach `text`/`author` — they become `null` and `flags.deleted` flips `true`.

**Commerce, places & apps archetypes** (DataForSEO-backed platforms):

- **Product** — Amazon, Google Shopping (title, price, rating, brand, images, specifications, variant ids).
- **Review** — shared across Amazon, Google Shopping, Trustpilot, Tripadvisor, Google Business, Google Play, Apple App Store (`id`, `title`, `text`, `author`, `rating`, `helpful_votes`, `published_at`, `source`, `responses[]` for owner/developer replies, `images`).
- **Seller** — Amazon, Google Shopping per-seller offers (name, price, condition, rating).
- **Place** — Tripadvisor, Google Business (name, category, rating, reviews_count, price_level, phone, latitude/longitude, image_urls; Google hotel results add a `place.hotel` block with amenities, sentiment topics, and multi-vendor prices).
- **App** — Google Play + Apple App Store share one App object with a `store` discriminator (`"google_play"` / `"app_store"`); store-exclusive fields (`installs`/`genres` on Google, `languages`/`advisories` on Apple) are null on the other store.

List endpoints return `{ items: [...], next_cursor?, total? }` regardless of the upstream's original key names. Commerce/place/app list items carry no `computed` block.

Research/analytics endpoints (Tavily, Perplexity, Polymarket, Content Analysis aggregates, twitter ai-search) are passthrough — they keep their upstream's native top-level keys.

## Computed Fields

When a field map applies (ScrapeCreators-backed Author/Post endpoints), four derived signals are added under `data.computed`:

| Field | Type | Author formula | Post formula |
|-------|------|---------------|-------------|
| `engagement_rate` | `number \| null` | `likes_count / followers` (clamped `[0, 1]`) | `(likes + comments + shares) / views` (clamped `[0, 1]`) |
| `language` | `string \| null` | ISO 639-1 detected from `bio` | ISO 639-1 detected from `post.content.text` |
| `content_category` | `string` | Keyword-based (15 categories) | Keyword-based (15 categories) |
| `estimated_reach` | `number \| null` | `round(followers * engagement_rate * 0.1)` | `round(views * 1.2)` when `views > 0`, else `null` |

`engagement_rate` returns `null` when the divisor or numerator is missing/zero (never `Infinity`, `NaN`, or negatives). Ratios >1.0 are clamped to 1.0 with a `_warnings` entry. Language detection needs ≥10 chars of text, else `null`.

## Response Warnings (`data._warnings`)

Successful responses may include an optional `data._warnings: string[]` with non-fatal notices (field-map drift, clamped computed values). **Advisory only** — do not flip success, gate retries, or treat it as an error. Empty arrays are omitted.

## Parameter Validation

Every request is validated **before any credit is deducted**:

1. **Required params** — every required name must be present and non-empty.
2. **`oneOf` groups** — endpoints like `GET /v1/youtube/channel` accept `channelId` / `handle` / `url`; at least one member must be present. Reference files render these as "At least one of `a` / `b` is required."
3. **Optional params** — forwarded to upstream only when provided.
4. **Per-platform format validators** — handles, URLs, subreddits, ASINs (10-char alphanumeric), and URL batches are checked against platform-specific rules at the boundary. Garbage is rejected in <100ms with no charge.

A failing request returns `400 INVALID_REQUEST` with `Missing required parameter(s): ...` or a format message.

## Pagination

List responses use `{ items, next_cursor?, total? }`. **Most list endpoints paginate** (cursor-based for nearly all platforms; offset-based on Naver):

- **Cursor-based**: pass `next_cursor` back verbatim (don't decode or trim it) in the platform's cursor param — `max_cursor` (TikTok), `continuationToken` (YouTube), `next_max_id` (Instagram, Truth Social), `after` (Reddit), `paginationToken`/`cursor` (LinkedIn), `cursor` (most others). Stop when `next_cursor` is absent.
- **Offset-based** (Naver only): increment `start` yourself (1-indexed, cap 1000) with `display` page size.
- Page size is upstream-decided (10–30 items typical). `total` may be exact, estimated, or missing — use `next_cursor` to decide when to stop, not `total`.

## Raw Format

Add `?format=raw` to any ScrapeCreators-backed endpoint to receive the original upstream response without unified-schema transformation or computed fields:

```bash
curl -s -H "x-api-key: $SOCIALCRAWL_API_KEY" \
  "https://www.socialcrawl.dev/v1/tiktok/profile?handle=charlidamelio&format=raw"
```

`?format=raw` is a no-op on non-ScrapeCreators platforms (GitHub, Hacker News, Tavily, Polymarket, Perplexity, Naver, Amazon, Google Shopping, Google Trends, Trustpilot, Tripadvisor, Google Business, Google Play, App Store, Content Analysis, Web, Pinterest url-stats, twitter ai-search) — there is no transform pipeline to bypass.

## Caching

Responses are cached by deterministic key (platform + resource + sorted query params). Cache category TTLs:

| Category | TTL |
|----------|-----|
| profile | 15 min |
| post | 10 min |
| comments | 5 min |
| search | 2 min |
| analytics | 30 min |

**Cache hits are free** — 0 credits, `X-Cache: HIT`, `cached: true`. If a cached body is empty (resource deleted since), you get `404 RESOURCE_NOT_FOUND` at no charge. SSE streaming requests to `/v1/search/everywhere` skip the cache entirely.

## Idempotent Retries

Any `/v1/*` call can be made safely retryable by sending an `Idempotency-Key` header (UUIDv4 or any opaque 16+ char string):

| Outcome | HTTP | Credits | Notes |
|---------|------|---------|-------|
| First call | (normal) | cost | Response stored; 24h TTL |
| Replay (same key, same params) | 200 with stored body | 0 | `X-Idempotent-Replay: true` |
| Payload mismatch (same key, different params) | 422 `IDEMPOTENCY_KEY_PAYLOAD_MISMATCH` | 0 | Use a fresh key |
| Conflict (same key, different account) | 409 `IDEMPOTENCY_KEY_CONFLICT` | 0 | Pick a new key |

Requests without the header skip this subsystem. SSE streaming requests cannot be replayed — replays serve the cached sync envelope (or 409 if none exists).

## Concurrency Limit

50 concurrent requests per API key. The 51st returns `429 CONCURRENCY_LIMIT` (no charge).

## Task-Polled Platforms (latency note)

Google Shopping, Trustpilot, Tripadvisor, most Google Business resources, and most Google Play / App Store resources run on a task-queue upstream. The API hides this behind a normal synchronous call, but expect **~10–45 seconds** of latency on those endpoints. Plan timeouts accordingly (60s is safe).

## Universal Search (`/v1/search/everywhere`)

Flat **20 credits** per call. Fans out across up to 15 sources in parallel (reddit, twitter-ai-search, youtube, tiktok, instagram, hackernews, polymarket, github, threads, pinterest, perplexity, tavily + tiktok/instagram/youtube hashtag siblings in hashtag mode), then fuses, reranks, enriches with top comments, and clusters the results.

Two response modes via the `Accept` header:

- `application/json` (default) — standard envelope with the full ranked result set.
- `text/event-stream` — typed SSE chunks: `meta`, `source_started`, `items`, `source_failed`, `plan_refined`, `ranked_partial`, `ranked_final`, `comments_enriched`, `clusters`, `warning`, `done`, `error`.

Fully refunded when every source fails or returns empty (sync and streaming both).

## Prism Composites (`/v1/prism/*`)

Server-side composites that fan out to several detail endpoints and fold the legs into one unified payload behind the standard envelope. Every composite emits a `legs[]` transparency array (`{endpoint, status, credits_used, latency_ms, error}`). Cross-platform recipes live under `/v1/prism/*`; a few keep their platform's own path and carry a `family: "prism"` flag (`{tiktok,instagram,youtube,twitter,facebook,linkedin}/profile/full`, `reddit/omni-search`). Pricing is flat or metered per recipe (0–50 credits); metered composites (e.g. `prism/comments`, `prism/ai-visibility`) deduct an upfront ceiling and refund to the actual work done. Streaming composites (`prism/comments`, `reddit/omni-search`) also support `Accept: text/event-stream`. Full list: [prism.md](prism.md).

## Monitors (`/v1/monitors/*`)

A stateful, scheduled wrapper: a monitor re-runs any registered recipe or Prism composite on a cadence (hourly/daily/weekly/cron), delivers each result to an HMAC-signed webhook, evaluates alert rules, and accumulates a per-run time-series. Monitors are **not** registry endpoints (not counted in the 357) and use POST/GET/PATCH/DELETE. Managing them costs 0 credits; each scheduled run bills the recipe's normal cost plus a 1-credit scheduling premium. Full contract: [monitors.md](monitors.md).

## Platform Status

```bash
curl -s "https://www.socialcrawl.dev/v1/status"
```

Returns per-platform circuit-breaker health. Each platform's breaker opens after 5 failures in 60s and stays open for 30s — during that window requests return `503` with `Retry-After: 30` and full refund.

## Error Codes

| Code | Status | Description | Credits |
|------|--------|-------------|---------|
| MISSING_API_KEY | 401 | No x-api-key header | Not charged |
| INVALID_API_KEY | 401 | Key malformed, not found, or revoked | Not charged |
| INSUFFICIENT_CREDITS | 402 | Balance too low | Not charged |
| INVALID_REQUEST | 400 | Missing required params OR malformed handle/URL/ASIN (format validator) | Not charged |
| METHOD_NOT_ALLOWED | 405 | Non-GET request on `/v1/*`. Response includes `Allow: GET`. | Not charged |
| ENDPOINT_NOT_FOUND | 404 | Unknown platform or resource | Not charged |
| RESOURCE_NOT_FOUND | 404 | Item not found on platform (includes empty-upstream guard) | Refunded |
| IDEMPOTENCY_KEY_CONFLICT | 409 | `Idempotency-Key` owned by a different account | Not charged |
| IDEMPOTENCY_KEY_PAYLOAD_MISMATCH | 422 | `Idempotency-Key` reused with different params | Not charged |
| CONCURRENCY_LIMIT | 429 | Over 50 concurrent requests per key | Not charged |
| UPSTREAM_ERROR | 502 | Platform returned an error | Refunded |
| SERVICE_UNAVAILABLE | 503 | Circuit breaker open (retry in 30s) or endpoint soft-disabled | Refunded / not charged |
| INTERNAL_ERROR | 500 | Unexpected server error | Refunded |

Error envelopes include a `doc_url` pointing at `https://www.socialcrawl.dev/docs/errors/<code>`.
