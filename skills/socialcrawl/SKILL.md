---
name: socialcrawl
description: >
  Interact with the SocialCrawl API — a unified social, commerce, and research
  data API covering 44 platforms and 357 endpoints, plus cross-platform Prism
  composites and scheduled Monitors. Fetch profiles, posts, comments, search
  results, transcripts, ad libraries, product/app/business reviews, places,
  prediction markets, news, finance quotes, Google Trends, web scraping/search,
  AI-grounded answers, and a universal cross-platform search from TikTok,
  Instagram, YouTube, Twitter/X, Facebook, Reddit, Amazon, Google Play, the App
  Store, Trustpilot, GitHub, Naver, and many more through a single API. Use when
  the user wants to: (1) fetch social
  media, commerce, app-store, or review data, (2) generate code that calls the
  SocialCrawl API, (3) understand SocialCrawl endpoints, parameters, pricing,
  or capabilities, (4) check their SocialCrawl credit balance, (5) run a
  universal search across many sources with one call, (6) run a cross-platform
  Prism composite or schedule a Monitor, or mentions "SocialCrawl",
  "social crawl", or "social media API".
---

# SocialCrawl API

Unified social media, commerce, and research data API. One API key, one response format, **44 platforms, 357 endpoints** — plus cross-platform **Prism** composites and stateful scheduled **Monitors**. Author and Post responses are normalized through platform field maps and augmented with computed fields (`engagement_rate`, `language`, `content_category`, `estimated_reach`) under `data.computed`. Commerce, review, place, and app endpoints share first-class canonical Product / Review / Seller / Place / App schemas. List responses are always `{ items, next_cursor?, total? }`. Add `?format=raw` to bypass the transform pipeline.

## API Key

Resolve the API key before making any call, checking these sources in order:

1. **Env var**: `echo "$SOCIALCRAWL_API_KEY"` — if set and starts with `sc_` (and is not a placeholder like `sc_your_api_key_here`), use it.
2. **Config file**: `cat ~/.config/socialcrawl/api_key 2>/dev/null` — if the file exists and contains a key starting with `sc_`, use it.
3. **Ask the user**: If neither source has a valid key:
   - Tell the user: "I need your SocialCrawl API key to continue. You can find it at https://socialcrawl.dev/dashboard — every account starts with 100 free credits."
   - Ask them to paste their key.
   - After receiving the key, **auto-save it** so they never need to paste it again:
     ```bash
     mkdir -p ~/.config/socialcrawl && echo "sc_xxxxx" > ~/.config/socialcrawl/api_key
     ```
   - Tell the user: "I've saved your key to `~/.config/socialcrawl/api_key` so it will be available in future sessions."

For all subsequent API calls in the session, use the resolved key directly in the curl command (do not rely on the env var being set).

## First Use

On the first interaction with this skill in a session:

1. Briefly introduce: "SocialCrawl provides a single API for 44 social, commerce, and research platforms (357 endpoints, plus Prism composites and Monitors). Let me verify your API key."
2. Resolve the API key using the steps above. If the key is missing or a placeholder, stop here and ask for it before proceeding.
3. Verify it with the free balance endpoint (0 credits):
   ```bash
   curl -s -H "x-api-key: KEY" "https://www.socialcrawl.dev/v1/credits/balance"
   ```
   (Replace `KEY` with the resolved key value.)
4. If successful, confirm the key works and show the balance. Then respond to whatever the user actually asked.
5. If it fails, report the error and help troubleshoot (see Error Handling below).

## Platforms

**Social media:**

| Platform | Endpoints | Reference |
|----------|-----------|-----------|
| TikTok | 20 | [references/tiktok.md](references/tiktok.md) |
| TikTok Shop | 5 | [references/tiktokshop.md](references/tiktokshop.md) |
| Instagram | 33 | [references/instagram.md](references/instagram.md) |
| YouTube | 28 | [references/youtube.md](references/youtube.md) |
| Facebook | 22 | [references/facebook.md](references/facebook.md) |
| Twitter/X | 8 | [references/twitter.md](references/twitter.md) |
| LinkedIn | 44 | [references/linkedin.md](references/linkedin.md) |
| Reddit | 7 | [references/reddit.md](references/reddit.md) |
| Threads | 5 | [references/threads.md](references/threads.md) |
| Pinterest | 5 | [references/pinterest.md](references/pinterest.md) |
| Bluesky | 3 | [references/bluesky.md](references/bluesky.md) |
| Spotify | 6 | [references/spotify.md](references/spotify.md) |
| Rumble | 5 | [references/rumble.md](references/rumble.md) |
| Kwai | 3 | [references/kwai.md](references/kwai.md) |
| Truth Social | 3 | [references/truthsocial.md](references/truthsocial.md) |
| Twitch | 4 | [references/twitch.md](references/twitch.md) |
| Snapchat | 1 | [references/snapchat.md](references/snapchat.md) |
| Kick | 1 | [references/kick.md](references/kick.md) |

**Commerce, reviews & places:**

| Platform | Endpoints | Reference |
|----------|-----------|-----------|
| Amazon | 5 | [references/amazon.md](references/amazon.md) |
| Google Shopping | 4 | [references/google_shopping.md](references/google_shopping.md) |
| Trustpilot | 2 | [references/trustpilot.md](references/trustpilot.md) |
| Tripadvisor | 2 | [references/tripadvisor.md](references/tripadvisor.md) |
| Google (SERP, ads, Business, hotels) | 10 | [references/google.md](references/google.md) |
| Google Finance (quotes, markets, tickers) | 3 | [references/google_finance.md](references/google_finance.md) |
| Google Trends (interest over time, rising) | 2 | [references/google_trends.md](references/google_trends.md) |

**App stores:**

| Platform | Endpoints | Reference |
|----------|-----------|-----------|
| Google Play | 9 | [references/google_play.md](references/google_play.md) |
| Apple App Store | 9 | [references/app_store.md](references/app_store.md) |

**Research, dev & data:**

| Platform | Endpoints | Reference |
|----------|-----------|-----------|
| GitHub | 12 | [references/github.md](references/github.md) |
| Hacker News | 4 | [references/hackernews.md](references/hackernews.md) |
| Naver (Korean search, 11 corpora + brief) | 12 | [references/naver.md](references/naver.md) |
| Tavily (web search/extract/crawl) | 4 | [references/tavily.md](references/tavily.md) |
| Perplexity (AI research) | 1 | [references/perplexity.md](references/perplexity.md) |
| Polymarket (prediction markets) | 1 | [references/polymarket.md](references/polymarket.md) |
| Content Analysis (brand mentions + sentiment) | 10 | [references/content_analysis.md](references/content_analysis.md) |
| Google News (news SERP search) | 1 | [references/google_news.md](references/google_news.md) |
| Web (scrape, search, crawl, map any URL) | 22 | [references/web.md](references/web.md) |
| Universal Search (all platforms at once) | 2 | [references/search.md](references/search.md) |

**Link-in-bio:**

| Platform | Endpoints | Reference |
|----------|-----------|-----------|
| Linktree | 1 | [references/linktree.md](references/linktree.md) |
| Linkbio | 1 | [references/linkbio.md](references/linkbio.md) |
| Linkme | 1 | [references/linkme.md](references/linkme.md) |
| Komi | 1 | [references/komi.md](references/komi.md) |
| Pillar | 1 | [references/pillar.md](references/pillar.md) |
| Utility (generic link page) | 1 | [references/utility.md](references/utility.md) |

**Composites & monitoring:**

| Surface | Endpoints | Reference |
|---------|-----------|-----------|
| Prism (cross-platform composites) | 33 | [references/prism.md](references/prism.md) |
| Monitors (scheduled recipes + webhooks) | — | [references/monitors.md](references/monitors.md) |

Prism endpoints (`/v1/prism/*`) fan out across many platforms and fold the legs into one report (URL lookup, comment harvesting, reputation, share-of-voice, AI consensus answers, crisis radar, creator vetting, video/app/product intelligence). A few composites keep their platform's own path (e.g. `{platform}/profile/full`, `reddit/omni-search`) and are documented in that platform's reference. Monitors (`/v1/monitors/*`) re-run any recipe on a cadence and deliver each result to a signed webhook — they are a stateful resource family, **not** registry endpoints, so they're not part of the 357 count and use POST/PATCH/DELETE in addition to GET.

## Workflow

Determine what the user wants, then follow the matching workflow:

**User wants data:**
1. Identify the platform and resource from their request
2. Read the platform's reference file from the table above
3. Resolve API key
4. Construct and execute the curl command
5. Return raw JSON response
6. Note `credits_used` and `credits_remaining` from the response

**User wants code:**
1. Identify platform, resource, and target language
2. Read the platform's reference file
3. Generate a working code snippet using `$SOCIALCRAWL_API_KEY` env var for the key
4. Present the code without executing

**User asks about capabilities:**
1. Answer from the platform table above
2. If they need details about auth, response format, unified schemas, pagination, caching, idempotency, or errors, read [references/api-overview.md](references/api-overview.md)

**User wants a cross-platform composite (one call, many platforms):**
1. Read [references/prism.md](references/prism.md) to pick the right `/v1/prism/*` recipe (or a `{platform}/profile/full` / `reddit/omni-search` per-platform composite)
2. Prism composites are priced flat or metered per recipe (0–50 credits) — mention the cost before calling
3. Resolve API key, call the endpoint, return the unified payload (note the `legs[]` transparency array)

**User wants to schedule/monitor a recipe over time:**
1. Read [references/monitors.md](references/monitors.md)
2. `POST /v1/monitors` with a `recipe`, `cadence`, and `webhook_url`; manage via list/get/runs/timeseries/pause/resume/delete
3. Managing monitors is free; each scheduled run bills the recipe's normal cost + a 1-credit scheduling premium

**User asks about pricing or credit costs:**
1. Read [references/pricing.md](references/pricing.md) — it has the exact credit cost for every one of the 357 endpoints, the tier system, credit packs, and refund rules
2. Per-endpoint costs are also listed inline in each platform reference file

**User asks about credits/balance:**
1. Resolve API key
2. Run: `curl -s -H "x-api-key: $SOCIALCRAWL_API_KEY" "https://www.socialcrawl.dev/v1/credits/balance"` (0 credits)
3. Return the balance
4. For a line-by-line credit ledger (deductions/refunds, newest first, cursor-paginated), use `curl -s -H "x-api-key: $SOCIALCRAWL_API_KEY" "https://www.socialcrawl.dev/v1/credits/transactions?limit=50"` (0 credits)

**Ambiguous platform:** If the user says "get profile for @nike" without specifying a platform, ask which platform they mean.

**Multi-platform requests:** Load each platform's reference file and make sequential calls — or suggest `/v1/search/everywhere` (20 credits) when the user wants one query across many platforms at once.

## Making API Calls

Base URL: `https://www.socialcrawl.dev`

All data endpoints are GET requests:

```
curl -s -H "x-api-key: $SOCIALCRAWL_API_KEY" \
  "https://www.socialcrawl.dev/v1/{platform}/{resource}?{param}={value}"
```

URL-encode parameter values that contain spaces or special characters.

The only exception is the Monitors family (`/v1/monitors/*`), which also uses POST/PATCH/DELETE with JSON bodies — see [references/monitors.md](references/monitors.md).

**Latency note:** Google Shopping, Trustpilot, Tripadvisor, Google Business, Google Play, and App Store endpoints are task-polled upstream — expect ~10–45s responses. Use a 60s timeout for those.

**Two-step endpoints:** some platforms require an id from a search call first — Google Shopping `product`/`reviews`/`sellers` need ids from `product-search`; Tripadvisor `reviews` needs `url_path` from `search`; Google `hotels/info` needs `hotel_identifier` from `hotels/search`. The reference files flag these.

## Credit Tiers

| Tier | Cost | Endpoints | Typical endpoints |
|------|------|-----------|-------------------|
| standard | 1 credit | 176 | Profiles, posts, search, comments, reference data |
| advanced | 5 credits | 90 | Ad libraries, trending, audience analytics, app data, reviews, Google Trends, LinkedIn social graph + jobs, Instagram relationship/discovery data |
| premium | 10 credits | 18 | Video transcripts, age-gender detection, LinkedIn people/job search + reactions, app listings search |
| custom (flat / metered) | varies (0–50) | 73 | `/v1/search/everywhere` (20) & `search/forums` (10); `naver/brief` (10); `{platform}/profile/full` (5); web scrape/crawl; all `/v1/prism/*` composites (0–50, flat or metered per recipe) |

Cache hits, idempotent replays, and `/v1/credits/balance` cost 0 credits. Failed calls (upstream errors, not-found resources) are auto-refunded. Metered composites deduct an upfront ceiling and refund down to the actual work done. Full per-endpoint pricing: [references/pricing.md](references/pricing.md).

Before executing an advanced (5), premium (10), universal-search (20), or Prism composite call, mention the credit cost to the user. After every call, report `credits_used` and `credits_remaining` from the response.

## Error Handling

| Code | Status | Action |
|------|--------|--------|
| MISSING_API_KEY | 401 | Ask user for their API key |
| INVALID_API_KEY | 401 | "Your API key appears invalid. Check your SocialCrawl dashboard." |
| INSUFFICIENT_CREDITS | 402 | "You're out of credits. Top up at socialcrawl.dev/dashboard/billing" |
| INVALID_REQUEST | 400 | Check required params and format rules in the platform reference file |
| ENDPOINT_NOT_FOUND | 404 | "That endpoint doesn't exist. Check the platform table above." |
| RESOURCE_NOT_FOUND | 404 | "That profile/post wasn't found on the platform. Credits were refunded." |
| IDEMPOTENCY_KEY_CONFLICT | 409 | Pick a new Idempotency-Key |
| IDEMPOTENCY_KEY_PAYLOAD_MISMATCH | 422 | Same key reused with different params — use a fresh key |
| CONCURRENCY_LIMIT | 429 | "Too many concurrent requests (50 max). Wait a moment and retry." |
| UPSTREAM_ERROR | 502 | "Platform temporarily unavailable. Credits were refunded." |
| SERVICE_UNAVAILABLE | 503 | "Platform circuit breaker is open or endpoint temporarily disabled. Try again in 30s. Credits refunded." |
| INTERNAL_ERROR | 500 | "Unexpected error. Credits were refunded." |

## References

- **[references/api-overview.md](references/api-overview.md)** — Read when user asks about authentication, response envelope, unified schemas (Author/Post/Comment/Product/Review/Seller/Place/App), computed fields, pagination, caching, idempotency, `?format=raw`, concurrency, or error details
- **[references/pricing.md](references/pricing.md)** — Read when user asks about pricing, credit costs, tiers, credit packs, or refunds; has the exact cost of all 357 endpoints
- **[references/prism.md](references/prism.md)** — Read when user wants a cross-platform composite (`/v1/prism/*`) — one call that fans out across many platforms
- **[references/monitors.md](references/monitors.md)** — Read when user wants to schedule a recipe to re-run on a cadence with webhook delivery (`/v1/monitors/*`)
- **[references/{platform}.md](references/)** — Read the specific platform file when user asks about or wants to call that platform's endpoints
