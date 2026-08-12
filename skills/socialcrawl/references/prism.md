# Prism

33 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 1 standard (1 credit), 32 custom (flat/metered) — the exact cost is in each endpoint heading below.

Prism composites are server-side recipes that fan out to several detail endpoints and fold the legs into one unified payload behind the standard envelope. Every composite emits a `legs[]` transparency array (`{endpoint, status, credits_used, latency_ms, error}`). Cross-platform recipes live under `/v1/prism/*`; a few keep their own platform path and carry `family: "prism"` (e.g. `{platform}/profile/full`, `reddit/omni-search`). Pricing is flat or **metered** per recipe (0–50 credits) — metered composites (e.g. `prism/comments`, `prism/ai-visibility`) deduct an upfront ceiling and refund down to the actual work done, so the response `credits_used` is the real charge. Streaming composites (`prism/comments`, `reddit/omni-search`) also accept `Accept: text/event-stream`. Mention the cost before calling any composite priced above 10 credits.

## GET /v1/prism/lookup — 0 credits (custom)

Universal URL dispatcher: any social/commerce URL → the right detail endpoint's unified response.

- `url` (required) — Absolute http(s) URL of the post / profile / product to resolve.
- `include` (optional, string) — CSV of optional flags to forward verbatim to the resolved endpoint (e.g. `trim`). Each member must be an optional param of that endpoint.

```bash
curl "https://www.socialcrawl.dev/v1/prism/lookup?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/comments — 1 credit (standard)

Every comment on a post, replies nested, server-paginated to completion.

- `url` (required) — Absolute http(s) URL of the post whose comments to harvest.
- `max` (optional, integer) — Stop after roughly this many top-level comments (1–5000, default 1000). Whole pages are returned, so the actual count can slightly exceed this. Drives billing and, for `sort=top`, the depth of the ranking scan.
- `replies` (optional, boolean) — Expand replies for comments that have them, where the platform supports it (default true; TikTok/YouTube/Facebook only). Pair with `replies=false` when you only want the top comments.
- `cursor` (optional, string) — Opaque composite cursor from a prior response's `next_cursor` to resume harvesting.
- `sort` (optional, enum: top | recent) — `recent` (default — natural order) or `top` (most-liked first, ranked by each comment's like count). With `top`, the response adds `sorted_by: "likes_desc"`.
- `limit` (optional, integer) — Cap on how many top-level comments to return after sorting/scanning (1–5000, defaults to `max`). Truncates only the returned set — never what was scanned or billed. The response reports `returned`.

```bash
curl "https://www.socialcrawl.dev/v1/prism/comments?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/brand-mentions — 50 credits (custom)

Brand mention volume time-series, sentiment split, top sources, and recent mentions for one keyword.

- `keyword` (required) — The brand or term to track. Wrap in quotes for exact-phrase semantics.
- `date_from` (required) — Window start (YYYY-MM-DD). Required by the trend leg.
- `date_to` (optional, string) — Window end (YYYY-MM-DD). Defaults to the latest crawl.
- `date_group` (optional, enum: day | week | month) — Trend bucket size: day (default), week, or month.
- `page_type` (optional, enum: ecommerce | news | blogs | message-boards | organization) — Optional surface filter: ecommerce, news, blogs, message-boards, or organization.
- `include` (optional, string) — Set `digest` to add an LLM narrative summary leg.

```bash
curl "https://www.socialcrawl.dev/v1/prism/brand-mentions?keyword=socialcrawl" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/demand-signals — 30 credits (custom)

Consumer-demand nowcast: app-review velocity, web mention slope, Reddit velocity, and commerce review levels, fused into a published demand index.

- `keyword` (required) — The brand or product to nowcast. Drives the mention, Reddit, and Amazon legs.
- `google_play_id` (optional, string) — Google Play package name (e.g. com.spotify.music) for the app-review velocity axis.
- `app_store_id` (optional, string) — Apple App Store numeric id for the app-review velocity axis.
- `signals` (optional, string) — CSV subset of app_reviews,mentions,reddit,commerce (default all). app_reviews is dropped when no app id is supplied.
- `amazon_query` (optional, string) — Override the Amazon product-search term if it differs from the brand.
- `country` (optional, string) — Location for the app-review legs (default United States); a 2-letter code is also applied to the Amazon leg.
- `date_from` (optional, string) — Window start (YYYY-MM-DD) for the mention-slope leg. Defaults to 30 days ago.
- `date_to` (optional, string) — Window end (YYYY-MM-DD). Defaults to today.
- `depth` (optional, integer) — Reviews per store for the velocity computation (1-600, default 150).

```bash
curl "https://www.socialcrawl.dev/v1/prism/demand-signals?keyword=spotify" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/campaign — 35 credits (custom)

Campaign tracker: pre/during/post volume lift, cross-platform engagement, and ranked top amplifiers for a hashtag or phrase.

- `hashtag` (optional, string) — The campaign hashtag (with or without #). One of hashtag or phrase is required.
- `phrase` (optional, string) — A campaign slogan/phrase instead of a hashtag. One of hashtag or phrase is required.
- `window_start` (optional, string) — Campaign launch date (YYYY-MM-DD) — the pre/during boundary. Optional; defaults to 30 days ago.
- `window_end` (optional, string) — Campaign end date (YYYY-MM-DD) — the during/post boundary. Defaults to today.
- `pre_days` (optional, integer) — Baseline days before window_start for lift measurement (1-90, default 14).
- `post_days` (optional, integer) — Days after window_end for the post window (0-90, default 14; 0 = no post window).
- `include` (optional, string) — Set amplifier_dates to date YouTube amplifiers via direct youtube/video calls (undated in fusion).

**At least one of `hashtag` / `phrase` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/prism/campaign" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/ai-visibility — 2 credits (custom)

AI Share-of-Voice / GEO monitoring: prompt set x reruns to per-brand appearance-% per AI engine plus a cited-domain ranking.

- `brand` (optional, string) — The brand whose appearance-% is measured (required). Matched against each answer plus its aliases.
- `prompts` (optional, string) — The category prompts to probe, as a JSON array or a pipe-delimited list (1-20). One of prompts or topic is required.
- `topic` (optional, string) — A topic probed as a single prompt in v1 (one of prompts or topic is required).
- `competitors` (optional, string) — CSV of up to 5 competitors also measured for appearance-% from the same answers.
- `engines` (optional, string) — CSV subset of perplexity,grok (default both) — the grounded-answer engines probed.
- `runs` (optional, integer) — Reruns per (prompt, engine) to measure variance (1-20, default 8).
- `preset` (optional, enum: quick | standard | deep) — quick|standard|deep — sets runs and caps prompts for a flat probe budget.
- `include` (optional, string) — Set web_baseline to cross-join AI-cited domains against your web top domains.
- `brand_domains` (optional, string) — CSV of your own domains so the citation ranking can flag the ones you already rank on.

```bash
curl "https://www.socialcrawl.dev/v1/prism/ai-visibility" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/crisis-postmortem — 35 credits (custom)

Crisis post-mortem: a who-said-what-first timeline across web, Reddit, Hacker News, and social, with an origin, peak, propagation sequence, and a grounded narrative.

- `brand` (required) — The brand or entity the crisis is about (required).
- `window_start` (optional, string) — Start of the crisis window (YYYY-MM-DD) — the earliest point on the timeline. Optional; defaults to 30 days ago.
- `window_end` (optional, string) — End of the crisis window (YYYY-MM-DD). Defaults to today.
- `crisis_terms` (optional, string) — Optional CSV of up to 5 terms (e.g. recall,defect) that scope the legs to the actual incident.
- `include` (optional, string) — narrative (default on) adds the grounded LLM propagation narrative; pass an empty value for the raw timeline only.

```bash
curl "https://www.socialcrawl.dev/v1/prism/crisis-postmortem?brand=acme" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/crisis-radar — 15 credits (custom)

Stateless crisis breach check: a z-score on daily mention volume and negative share, with on-breach confirmation and a severity grade.

- `brand` (optional, string) — The brand to watch (required).
- `sensitivity` (optional, string) — Z-score breach threshold (0.5-6, default 2.0). z>=sensitivity on volume or negative-share fires a breach.
- `confirm` (optional, boolean) — true -> on a breach, run the escalation legs and grade severity (+30 credits, charged only when a breach fires).
- `baseline_days` (optional, integer) — Rolling-mean window for the z-score (3-30, default 7).
- `date_to` (optional, string) — The day being evaluated (YYYY-MM-DD). Defaults to today.

```bash
curl "https://www.socialcrawl.dev/v1/prism/crisis-radar" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/devtool-pulse — 20 credits (custom)

Developer-brand health: a devtool's repo dossier + Hacker News reaction + Reddit chatter + dev-blog echo, in one call.

- `query` (required) — The devtool name to sweep across Hacker News, Reddit, and the dev-blog index (e.g. Bun, Drizzle ORM, tRPC).
- `repo` (optional, string) — The repo to dossier — owner/repo or a github.com/{owner}/{repo} URL. Recommended for a precise dossier.
- `subreddit` (optional, string) — Optional scope for the Reddit leg (bare name, no r/) — switches it to a subreddit search.
- `include` (optional, string) — CSV subset of dossier,hn,reddit,blogs (default all). Trims which legs run, not the flat price.
- `date_from` (optional, string) — Optional window start (YYYY-MM-DD) applied to the time-bounded legs.
- `date_to` (optional, string) — Optional window end (YYYY-MM-DD).

```bash
curl "https://www.socialcrawl.dev/v1/prism/devtool-pulse?query=Bun" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/leads — 50 credits (custom)

Ranked feed of public conversations where people seek alternatives to or are switching from a competitor.

- `competitor` (required) — The competitor/product to mine alternative-seeking conversations for (≤80 chars).
- `product_category` (optional, string) — Optional disambiguator appended to the social queries to cut cross-domain noise (e.g. 'project management').
- `freshness` (optional, string) — Recency floor — Nd/Nw/Nm (e.g. 30d) or an ISO date. Default 30d.
- `include` (optional, string) — Set `comments` to attach top-thread Reddit comments to the top leads.
- `limit` (optional, integer) — Max leads in the fused feed (1–100, default 50).

```bash
curl "https://www.socialcrawl.dev/v1/prism/leads?competitor=notion" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/earned-media — 25 credits (custom)

A brand's earned-media footprint — news + tech-press + fresh-web clips, deduped and ranked, with an outlet-coverage rollup.

- `brand` (required) — The brand/company to map earned media for.
- `competitor` (optional, string) — Optional competitor for a share-of-coverage gap.
- `date_from` (optional, string) — Window start (YYYY-MM-DD).
- `date_to` (optional, string) — Window end (YYYY-MM-DD).
- `min_domain_rank` (optional, integer) — Drop clips from sites below this domain authority.
- `include` (optional, string) — Set `digest` to add an LLM narrative summary.

```bash
curl "https://www.socialcrawl.dev/v1/prism/earned-media?brand=Vercel" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/truthsocial-pulse — 20 credits (custom)

A Truth Social handle's pulse — profile, recent posts, per-post detail drill, and the news echo, in one call.

- `handle` (required) — The Truth Social handle (no @).
- `drill` (optional, integer) — How many top posts to drill for full detail (0 to skip).
- `posts` (optional, integer) — How many recent posts to pull (window cap).
- `news_query` (optional, string) — Override the content_analysis news keyword (defaults to the handle/display name).
- `include` (optional, string) — CSV subset of posts,news to trim which legs run.
- `cursor` (optional, string) — Opaque pagination cursor for the posts leg.

```bash
curl "https://www.socialcrawl.dev/v1/prism/truthsocial-pulse?handle=realDonaldTrump" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/launch-echo — 20 credits (custom)

How a launch landed — the Hacker News reaction (top threads + comments), the dev-blog echo, and an optional repo dossier.

- `query` (required) — The launch/product name to measure reception for.
- `repo` (optional, string) — Optional owner/repo or github URL to anchor the dossier.
- `threads` (optional, integer) — How many top HN threads to dig comments for.
- `date_from` (optional, string) — Window start (YYYY-MM-DD).
- `date_to` (optional, string) — Window end (YYYY-MM-DD).
- `include` (optional, string) — CSV subset toggling the comments/blogs/dossier legs.

```bash
curl "https://www.socialcrawl.dev/v1/prism/launch-echo?query=Bun 1.2" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/audience-overlap — 20 credits (custom)

How much two TikTok creators' commenter audiences overlap — Jaccard, shared-fan count, and a confidence label.

- `handle_a` (required) — First TikTok creator handle.
- `handle_b` (required) — Second TikTok creator handle.
- `platform` (optional, string) — Platform (tiktok only in v1; default tiktok).
- `videos_per_creator` (optional, integer) — Recent videos sampled per creator (1–10, default 5) — caps the commenter pull.
- `depth` (optional, string) — Set `deep` to widen the shared-fan enrichment sample.

```bash
curl "https://www.socialcrawl.dev/v1/prism/audience-overlap?handle_a=mkbhd" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/reputation — 30 credits (custom)

A brand's cross-source reputation — Trustpilot + app stores + Google Business + web sentiment, blended into one weighted score with themed pros/cons.

- `brand` (required) — The brand/business/domain to assess.
- `sources` (optional, string) — CSV subset of trustpilot,google_play,app_store,google,tripadvisor,web (default the core set).
- `country` (optional, string) — Marketplace/locale (DFS location). Defaults to United States.
- `depth` (optional, integer) — Reviews per source (Trustpilot clamped ≤20).
- `place` (optional, string) — Set to enable the place-based legs (Google Business + TripAdvisor).
- `axis` (optional, enum: company | product | both) — Which reputation axis to headline: company, product, or both (default).
- `app_store_id` (optional, string) — App Store id to anchor that axis directly (skips resolver).
- `google_play_id` (optional, string) — Google Play id to anchor that axis directly (skips resolver).
- `include` (optional, string) — Optional leg toggles.

```bash
curl "https://www.socialcrawl.dev/v1/prism/reputation?brand=Notion" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/employer-brand — 30 credits (custom)

A company's employer brand — what people say about working there across Reddit, the web, YouTube, Naver, and the company's own LinkedIn voice.

- `company` (required) — The employer/company name.
- `linkedin_url` (optional, string) — The company's LinkedIn URL — enables the LinkedIn voice axis + the posting-vs-reality gap.
- `surfaces` (optional, string) — CSV subset of the surfaces to include.
- `phrases` (optional, string) — Optional extra Reddit search phrases.
- `timeframe` (optional, string) — Reddit timeframe window.
- `date_from` (optional, string) — Window start (YYYY-MM-DD).
- `date_to` (optional, string) — Window end (YYYY-MM-DD).

```bash
curl "https://www.socialcrawl.dev/v1/prism/employer-brand?company=Stripe" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/audience-questions — 30 credits (custom)

The real questions a topic's audience asks — harvested from Reddit + YouTube threads and clustered by intent (who/what/why/how/vs).

- `topic` (required) — The topic/keyword to mine audience questions for.
- `platforms` (optional, string) — CSV subset of reddit,youtube,web (default reddit,youtube).
- `max_questions` (optional, integer) — Cap on questions returned.
- `threads_per_source` (optional, integer) — How many top threads to dig per source.
- `timeframe` (optional, string) — Recency window.
- `include` (optional, string) — Set `web` to add the universal-search leg.

```bash
curl "https://www.socialcrawl.dev/v1/prism/audience-questions?topic=kubernetes operators" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/product-reviews — 30 credits (custom)

A product's reviews across Amazon + Google Shopping + Trustpilot, folded into a cross-marketplace rating + themed pros/cons report.

- `query` (optional, string) — Product name to auto-resolve across marketplaces.
- `asin` (optional, string) — Amazon ASIN to anchor the Amazon axis directly.
- `gid` (optional, string) — Google product id (gid) to anchor the Google Shopping axis (NOT the catalogid).
- `sources` (optional, string) — CSV subset of amazon,google_shopping,trustpilot (default all).
- `country` (optional, string) — Marketplace country (DFS location).
- `depth` (optional, integer) — Reviews per source (Trustpilot clamped ≤20).
- `competitors` (optional, string) — Optional competitor products for a comparison (validated; deeper sweep is a fast-follow).
- `include` (optional, string) — Optional leg toggles.

**At least one of `query` / `asin` / `gid` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/prism/product-reviews" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/apps-lookup — 30 credits (custom)

One app across Google Play + the App Store — resolved, title-matched, and compared into a cross-store rating + listing report.

- `title` (optional, string) — The app title to resolve across both stores.
- `google_play_id` (optional, string) — Google Play app id to anchor that store directly.
- `app_store_id` (optional, string) — App Store app id to anchor that store directly.
- `stores` (optional, string) — CSV subset of google_play,app_store (default both).
- `country` (optional, string) — Store country.
- `language` (optional, string) — Store language.
- `match_threshold` (optional, string) — Title-similarity threshold for the cross-store match guard (0–1, default 0.6).
- `include` (optional, string) — Optional leg toggles.

**At least one of `title` / `google_play_id` / `app_store_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/prism/apps-lookup" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/org-radar — 26 credits (custom)

A GitHub org's footprint — its top repos each expanded into a full dossier (releases, issue load, top request/complaint), rolled up.

- `org` (required) — The GitHub org login or a github.com/{org} URL.
- `repos` (optional, integer) — How many top repos to dossier (1–10, default 5) — drives the metered price.
- `sort` (optional, enum: stars | updated | pushed) — Repo ranking: stars (default), updated, or pushed.
- `include` (optional, string) — Optional leg toggles.

```bash
curl "https://www.socialcrawl.dev/v1/prism/org-radar?org=vercel" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/creator-vet — 50 credits (custom)

Vet a creator before partnering — engagement quality, commenter authenticity, posting cadence, and controversy signals, optionally across platforms.

- `handle` (required) — The creator handle to vet.
- `platform` (optional, string) — Primary platform (tiktok/youtube/instagram).
- `depth` (optional, string) — Set `deep` to widen the post + commenter sample.
- `include` (optional, string) — Set `cross_platform` to add the universal cross-platform presence leg (+25cr).

```bash
curl "https://www.socialcrawl.dev/v1/prism/creator-vet?handle=mkbhd" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/korea-gap — 40 credits (custom)

What the world is talking about that Korea isn't (and vice versa) — the global vs Korean (Naver) conversation gap for a brand/topic.

- `query` (required) — The brand/topic to compare across the global and Korean conversations.
- `include` (optional, string) — Members include `social` (the everywhere leg) + `digest`. Drop `social` for the 15cr web-only variant.
- `date_from` (optional, string) — Window start (YYYY-MM-DD).
- `date_to` (optional, string) — Window end (YYYY-MM-DD).
- `display` (optional, integer) — Naver results per corpus.

```bash
curl "https://www.socialcrawl.dev/v1/prism/korea-gap?query=Stanley cup" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/share-of-voice — 40 credits (custom)

Engagement-weighted Share of Voice across 2-5 brands, with web+social split, emotion overlay, and ESOV.

- `brands` (required) — 2-5 competitor brand names (CSV).
- `category_code` (optional, string) — Numeric DFS taxonomy code for true-share-of-category (use content_analysis/categories to look one up).
- `market_shares` (optional, string) — JSON map of real market share per brand (fraction or %), e.g. {"notion":0.4,"coda":0.25,"airtable":0.35}, to compute ESOV.
- `include` (optional, string) — CSV toggles (default `emotions,social`). Drop `social` for the cheaper web-only variant; drop `emotions` to skip the sentiment leg.
- `page_type` (optional, enum: ecommerce | news | blogs | message-boards | organization) — Optional surface filter forwarded to the content_analysis legs.
- `date_from` (optional, string) — Window start (YYYY-MM-DD). Defaults to 90 days ago.
- `date_to` (optional, string) — Window end (YYYY-MM-DD). Defaults to today.

```bash
curl "https://www.socialcrawl.dev/v1/prism/share-of-voice?brands=notion,coda,airtable" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/review-integrity — 30 credits (custom)

Cross-source review integrity verdict (statistical, deterministic).

- `query` (optional, string) — Product or brand name to evaluate.
- `asin` (optional, string) — Amazon ASIN to anchor the Amazon axis directly (skips product-search).
- `gid` (optional, string) — Google product id (gid) to anchor the Google Shopping axis (NOT the catalogid product.id).
- `sources` (optional, string) — CSV subset of amazon,google_shopping,trustpilot,web,forums (default all).
- `country` (optional, string) — Marketplace country (DFS location). Defaults to United States.

**At least one of `query` / `asin` / `gid` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/prism/review-integrity" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/answers — 15 credits (custom)

Multi-engine AI consensus: one question → Perplexity + Grok + Tavily answers verbatim, merged citations, and an agreement matrix.

- `query` (required) — The question, forwarded verbatim to every engine.
- `engines` (optional, string) — CSV subset of perplexity,grok,tavily (default all three).
- `include` (optional, string) — CSV of optional grounding legs: `polymarket` adds market probabilities (trimmed).

```bash
curl "https://www.socialcrawl.dev/v1/prism/answers?query=will the fed cut rates in september" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/video-intel — 5 credits (custom)

One video URL → detail + stats + transcript + top comments + commenter sample, across YouTube/TikTok/Rumble/Instagram.

- `url` (required) — Absolute http(s) URL of a YouTube, TikTok, Rumble, or Instagram video.
- `comments` (optional, string) — How many top comments to fetch (0–50, default 20). `0` skips the comments leg.
- `include` (optional, string) — CSV of optional costed legs: `transcript` (adds the dedicated transcript leg, +10cr, refunded when null) and/or `commenter_profiles` (≤3 commenter mini-profiles, TikTok/Instagram in v1).

```bash
curl "https://www.socialcrawl.dev/v1/prism/video-intel?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/voice — 5 credits (custom)

One person's public posts across X, Threads, Bluesky, and Truth Social, time-merged.

- `handle` (required) — The handle to look up across all four microblogs (a single leading @ is stripped).
- `platforms` (optional, string) — CSV subset of twitter,threads,bluesky,truthsocial (default all four).
- `cursor` (optional, string) — Opaque per-platform pagination token from a prior response's cursors_by_platform (twitter is a single non-paginatable page).
- `include` (optional, string) — CSV subset of posts_by_platform,merged_timeline,computed to trim the payload (posts_by_platform is always returned).

```bash
curl "https://www.socialcrawl.dev/v1/prism/voice?handle=nasa" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/app-reviews — 15 credits (custom)

Cross-store app review intelligence (Google Play + App Store) — translated, clustered, sentiment-scored.

- `google_play_id` (optional, string) — Google Play package name (e.g. com.spotify.music).
- `app_store_id` (optional, string) — App Store numeric app id (e.g. 324684580).
- `query` (optional, string) — App name to auto-resolve the top hit on each requested store (when no id is given).
- `country` (optional, string) — Storefront country (DFS location name or numeric code). Defaults to the DFS default location.
- `language` (optional, string) — Language code (e.g. en).
- `depth` (optional, integer) — Reviews per store (default 150 Google / 50 Apple, max 600). The App Store returns ~50 at depth 40.
- `stores` (optional, string) — CSV subset of google_play,app_store. Defaults to whichever ids/query resolve.
- `include` (optional, string) — CSV of topics,sentiment_timeline,feature_requests,responses (default all). Omitting topics+feature_requests skips the LLM step.

```bash
curl "https://www.socialcrawl.dev/v1/prism/app-reviews" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/creator-card — 5 credits (custom)

One handle, unified author cards across TikTok, Instagram, YouTube, X (and more).

- `handle` (required) — The handle to look up across every requested platform (a single leading @ is stripped).
- `platforms` (optional, string) — CSV subset of tiktok,instagram,youtube,twitter,threads,bluesky,truthsocial (default the first four). Unknown platforms are ignored.
- `include` (optional, string) — CSV subset of cards,totals to trim the payload (cards is always returned).

```bash
curl "https://www.socialcrawl.dev/v1/prism/creator-card?handle=mrbeast" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/handle-audit — 5 credits (custom)

Should you pull this handle? One call scores a handle across platforms, ranks the best ones, and projects the data volume + credit cost to pull it.

- `handle` (required) — The handle to audit across every requested platform. Accepts a bare handle, a leading @, or a full profile URL (the platform is sniffed from the host).
- `platforms` (optional, string) — CSV subset of tiktok,instagram,youtube,twitter,threads,bluesky,truthsocial (default the first four). Unknown platforms are ignored. Max 8.
- `sample` (optional, string) — Recent posts sampled per found platform for the engagement + activity metrics (default 10, max 25).

```bash
curl "https://www.socialcrawl.dev/v1/prism/handle-audit?handle=mrbeast" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/post-stats — 1 credit (custom)

Up to 100 mixed-platform post URLs → current engagement per URL, failed URLs refunded.

- `urls` (required) — JSON array of 1–100 absolute http(s) post URLs (mixed platforms allowed).
- `include` (optional, string) — CSV subset of views,likes,comments,shares,saves to trim each row's engagement block.

```bash
curl "https://www.socialcrawl.dev/v1/prism/post-stats?urls=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/comment-lookup — 2 credits (custom)

Re-check up to 25 known comments in one call — per-item results, failed items refunded.

- `items` (required) — JSON array of 1–25 lookup items. Each item is `{ "comment_url": "…" }` or `{ "platform": "tiktok"|"instagram", "post_url": "…", "comment_id": "…" }`, optionally with `parent_comment_id`, `position_hint`, and `deep_scan`.

```bash
curl "https://www.socialcrawl.dev/v1/prism/comment-lookup?items=[{"comment_url":"https://www.tiktok.com/@mrbeast/video/7654638524729216287?comment_id=7654640784985211670"},{"platform":"instagram","post_url":"https://www.instagram.com/p/CnpPou9hWqq/","comment_id":"18007013966365752"}]" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/prism/profiles — 1 credit (custom)

Up to 50 (platform, handle) pairs → one canonical Author per row, failed handles refunded.

- `items` (required) — JSON array of 1–50 items. Each item is `{ "platform": "tiktok", "handle": "@scout2015", "custom_id"?: "…" }`. `handle` accepts an @handle, a bare handle, or a pasted profile URL.

```bash
curl "https://www.socialcrawl.dev/v1/prism/profiles?items=[{"platform":"tiktok","handle":"@scout2015"},{"platform":"linkedin","handle":"williamhgates","custom_id":"vet-1"}]" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
