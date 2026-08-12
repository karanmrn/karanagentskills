# SocialCrawl Pricing Reference

Complete per-endpoint credit pricing for all 357 active endpoints across 44 platforms. Auto-derived from the live endpoint registry — the same registry the router uses to charge your balance.

## How billing works

- Every API call deducts credits from your balance **before** the upstream call, atomically. The response reports `credits_used` and `credits_remaining` (also in the `X-Credits-Used` / `X-Credits-Remaining` headers).
- **Cache hits are free** — a response served from cache costs 0 credits (`X-Cache: HIT`, `cached: true`).
- **Automatic refunds** — credits are refunded on upstream errors (502), circuit-breaker rejections (503), internal errors (500), and empty-upstream results (404 `RESOURCE_NOT_FOUND`). You only pay for calls that return real data.
- **Idempotent replays are free** — resending with the same `Idempotency-Key` returns the stored response at 0 credits.
- **Metered composites** — some Prism composites (e.g. `prism/comments`, `prism/ai-visibility`) deduct an upfront ceiling and auto-refund down to the actual work done; the response `credits_used` is the real charge.
- `GET /v1/credits/balance` and `GET /v1/credits/transactions` are always 0 credits.

## Credit tiers

Most endpoints sit on a simple 1 / 5 / 10 ladder. A set of bundle and fan-out endpoints use a **custom** override that bypasses the ladder (flat or metered per recipe).

| Tier | Cost per call | Endpoints | Typical endpoints |
|------|--------------|-----------|-------------------|
| standard | 1 credit | 176 | Profiles, posts, comments, search, reference data |
| advanced | 5 credits | 90 | Ad libraries, trending, audience analytics, app/business/place reviews, LinkedIn social graph + jobs |
| premium | 10 credits | 18 | Video transcripts, age-gender detection, LinkedIn people/job search + reactions, app-listings search |
| **custom (flat/metered)** | **varies (0–50)** | 73 | Prism composites, `{platform}/profile/full`, `search/everywhere` (20), `naver/brief` (10), web scrape/crawl |

Counted by underlying tier (custom endpoints folded into their base tier), the split is **210 standard · 117 advanced · 30 premium = 357**. Exact per-endpoint costs are in the tables below.

## Credit packs

| Plan | Credits | Price |
|------|---------|-------|
| Free (signup bonus) | 100 | £0 |
| Starter | 2,500 | £15 one-time |
| Growth | 20,000 | £49 one-time |
| Pro | 150,000 | £299 one-time |
| Enterprise | Custom | [Contact](https://socialcrawl.dev/contact) |

Current packs and any promotions: https://socialcrawl.dev/pricing

## Per-endpoint pricing

### Amazon (5)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/amazon/shop` | Get Amazon shop page | 1 (standard) |
| `/v1/amazon/product-search` | Search Amazon products by keyword | 1 (standard) |
| `/v1/amazon/product` | Get an Amazon product by ASIN | 5 (advanced) |
| `/v1/amazon/reviews` | Get Amazon product reviews | 5 (advanced) |
| `/v1/amazon/sellers` | Get Amazon sellers and offers for a product | 1 (standard) |

### Apple App Store (9)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/app_store/app-search` | Search Apple App Store apps by keyword | 5 (advanced) |
| `/v1/app_store/search-suggestions` | Get Apple App Store search suggestions | 1 (standard) |
| `/v1/app_store/app-info` | Get full Apple App Store app details | 5 (advanced) |
| `/v1/app_store/app-reviews` | Get Apple App Store reviews for an app | 5 (advanced) |
| `/v1/app_store/app-list` | Get an Apple App Store chart | 5 (advanced) |
| `/v1/app_store/app-listings-search` | Search the Apple App Store listings database (paginated) | 10 (premium) |
| `/v1/app_store/categories` | List Apple App Store app categories | 1 (standard) |
| `/v1/app_store/locations` | List supported Apple App Store storefront locations | 1 (standard) |
| `/v1/app_store/languages` | List supported Apple App Store languages | 1 (standard) |

### Bluesky (3)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/bluesky/profile` | Get a Bluesky profile | 1 (standard) |
| `/v1/bluesky/user/posts` | List a Bluesky user's posts | 1 (standard) |
| `/v1/bluesky/post` | Get a Bluesky post | 1 (standard) |

### Content Analysis (10)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/content_analysis/search` | Search web citations of a keyword with per-mention sentiment | 20 (custom) |
| `/v1/content_analysis/summary` | Aggregate mention summary for a keyword | 20 (custom) |
| `/v1/content_analysis/sentiment` | Sentiment breakdown for a keyword | 20 (custom) |
| `/v1/content_analysis/rating-distribution` | Rating histogram for a keyword | 20 (custom) |
| `/v1/content_analysis/phrase-trends` | Keyword mention volume + sentiment over time | 20 (custom) |
| `/v1/content_analysis/category-trends` | Category mention volume + sentiment over time | 20 (custom) |
| `/v1/content_analysis/languages` | List supported Content Analysis languages | 1 (standard) |
| `/v1/content_analysis/locations` | List supported Content Analysis locations | 1 (standard) |
| `/v1/content_analysis/categories` | List the Content Analysis category taxonomy | 1 (standard) |
| `/v1/content_analysis/filters` | List the filterable fields for Content Analysis | 1 (standard) |

### Facebook (22)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/facebook/profile` | Get Facebook page profile | 1 (standard) |
| `/v1/facebook/profile/posts` | List Facebook page posts | 1 (standard) |
| `/v1/facebook/post` | Get Facebook post details | 1 (standard) |
| `/v1/facebook/post/comments` | List Facebook post comments | 1 (standard) |
| `/v1/facebook/group/posts` | List Facebook group posts | 1 (standard) |
| `/v1/facebook/post/transcript` | Get Facebook video transcript | 10 (premium) |
| `/v1/facebook/profile/photos` | List Facebook profile photos | 1 (standard) |
| `/v1/facebook/profile/reels` | List Facebook profile reels | 1 (standard) |
| `/v1/facebook/adlibrary/ad` | Get Facebook Ad Library ad details | 5 (advanced) |
| `/v1/facebook/adlibrary/company/ads` | List Facebook Ad Library company ads | 5 (advanced) |
| `/v1/facebook/adlibrary/search/ads` | Search Facebook Ad Library | 5 (advanced) |
| `/v1/facebook/adlibrary/search/companies` | Search Facebook Ad Library companies | 5 (advanced) |
| `/v1/facebook/profile/events` | List a Facebook page's events | 1 (standard) |
| `/v1/facebook/post/comment/replies` | List replies to a Facebook post comment | 1 (standard) |
| `/v1/facebook/marketplace/location/search` | Search Facebook Marketplace locations | 1 (standard) |
| `/v1/facebook/marketplace/search` | Search Facebook Marketplace listings | 1 (standard) |
| `/v1/facebook/marketplace/item` | Get a Facebook Marketplace item | 1 (standard) |
| `/v1/facebook/events/search` | Search Facebook events by keyword | 1 (standard) |
| `/v1/facebook/events` | List Facebook events for a city | 1 (standard) |
| `/v1/facebook/event/details` | Get details for a Facebook event | 1 (standard) |
| `/v1/facebook/adlibrary/ad/transcript` | Get a Facebook Ad Library video ad transcript | 10 (premium) |
| `/v1/facebook/profile/full` | Facebook profile, recent posts, and computed analytics in one call. | 5 (custom) |

### GitHub (12)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/github/profile` | Get a GitHub user profile | 1 (standard) |
| `/v1/github/repo` | Get a GitHub repository | 1 (standard) |
| `/v1/github/profile/repos` | List a GitHub user's repositories | 1 (standard) |
| `/v1/github/repo/readme` | Get a repository's README | 1 (standard) |
| `/v1/github/repo/releases` | List a repository's releases | 1 (standard) |
| `/v1/github/repo/issues` | List a repository's issues (and PRs) | 1 (standard) |
| `/v1/github/issue` | Get a single issue or pull request | 1 (standard) |
| `/v1/github/issue/comments` | Get comments on an issue or pull request | 1 (standard) |
| `/v1/github/search` | Search GitHub issues and pull requests | 1 (standard) |
| `/v1/github/repo/top-issues` | Top feature request and top complaint for a repository | 5 (advanced) |
| `/v1/github/repo/dossier` | Full project dossier for a repository | 5 (advanced) |
| `/v1/github/user/profile-velocity` | User contribution velocity dossier | 10 (premium) |

### Google (10)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/google/search` | Google web search | 1 (standard) |
| `/v1/google/ad` | Get Google ad details | 5 (advanced) |
| `/v1/google/adlibrary/advertisers/search` | Search Google Ad Library advertisers | 5 (advanced) |
| `/v1/google/company/ads` | List Google ads by company | 5 (advanced) |
| `/v1/google/business/info` | Get a Google Business Profile | 1 (standard) |
| `/v1/google/business/extended-reviews` | Get Google extended (multi-source) reviews | 5 (advanced) |
| `/v1/google/business/updates` | Get Google Business Profile posts (updates) | 1 (standard) |
| `/v1/google/business/questions` | Get Google Business Profile questions & answers | 5 (advanced) |
| `/v1/google/hotels/search` | Search Google hotels | 1 (standard) |
| `/v1/google/hotels/info` | Get Google hotel detail | 5 (advanced) |

### Google Finance (3)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/google_finance/quote` | Get a financial instrument quote | 5 (advanced) |
| `/v1/google_finance/ticker-search` | Search financial instruments by name | 1 (standard) |
| `/v1/google_finance/markets` | Get a markets overview (indices + movers) | 1 (standard) |

### Google News (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/google_news/search` | Search Google News | 1 (standard) |

### Google Play (9)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/google_play/app-search` | Search Google Play apps by keyword | 5 (advanced) |
| `/v1/google_play/search-suggestions` | Get Google Play search suggestions | 1 (standard) |
| `/v1/google_play/app-info` | Get full Google Play app details | 5 (advanced) |
| `/v1/google_play/app-reviews` | Get Google Play reviews for an app | 5 (advanced) |
| `/v1/google_play/app-list` | Get a Google Play store chart | 5 (advanced) |
| `/v1/google_play/app-listings-search` | Search the Google Play listings database (paginated) | 10 (premium) |
| `/v1/google_play/categories` | List Google Play app categories | 1 (standard) |
| `/v1/google_play/locations` | List supported Google Play storefront locations | 1 (standard) |
| `/v1/google_play/languages` | List supported Google Play languages | 1 (standard) |

### Google Shopping (4)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/google_shopping/product-search` | Search Google Shopping products | 5 (advanced) |
| `/v1/google_shopping/product` | Get Google Shopping product detail | 1 (standard) |
| `/v1/google_shopping/reviews` | Get Google Shopping product reviews | 1 (standard) |
| `/v1/google_shopping/sellers` | Get Google Shopping sellers for a product | 1 (standard) |

### Google Trends (2)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/google_trends/explore` | Get Google Trends interest over time | 5 (advanced) |
| `/v1/google_trends/rising` | Get related + rising Google Trends queries | 5 (advanced) |

### Hacker News (4)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/hackernews/search` | Search Hacker News | 1 (standard) |
| `/v1/hackernews/story` | Get a Hacker News story | 1 (standard) |
| `/v1/hackernews/story/comments` | Get comments on a Hacker News story | 1 (standard) |
| `/v1/hackernews/profile` | Get a Hacker News user profile | 1 (standard) |

### Instagram (33)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/instagram/profile` | Get Instagram user profile | 1 (standard) |
| `/v1/instagram/profile/posts` | List Instagram user posts | 1 (standard) |
| `/v1/instagram/post` | Get Instagram post details | 1 (standard) |
| `/v1/instagram/post/comments` | List Instagram post comments | 5 (advanced) |
| `/v1/instagram/comment` | Look up one Instagram comment by URL or id | 5 (custom) |
| `/v1/instagram/basic-profile` | Get Instagram basic profile | 1 (standard) |
| `/v1/instagram/profile/reels` | List Instagram user reels | 1 (standard) |
| `/v1/instagram/highlights` | List Instagram story highlights | 1 (standard) |
| `/v1/instagram/highlight/detail` | Get Instagram highlight detail | 1 (standard) |
| `/v1/instagram/search/reels` | Search Instagram reels | 1 (standard) |
| `/v1/instagram/media/transcript` | Get Instagram media transcript | 10 (premium) |
| `/v1/instagram/user/embed` | Get Instagram user embed HTML | 1 (standard) |
| `/v1/instagram/audio/reels` | List Instagram reels using an audio track | 1 (standard) |
| `/v1/instagram/search/hashtag` | Search Instagram posts by hashtag | 5 (advanced) |
| `/v1/instagram/search/profiles` | Search Instagram profiles by keyword | 1 (standard) |
| `/v1/instagram/reels/trending` | Get trending Instagram reels | 5 (advanced) |
| `/v1/instagram/followers` | List Instagram followers | 5 (advanced) |
| `/v1/instagram/following` | List Instagram following | 5 (advanced) |
| `/v1/instagram/similar` | List similar Instagram accounts | 5 (advanced) |
| `/v1/instagram/post/likers` | List Instagram post likers | 5 (advanced) |
| `/v1/instagram/post/stats` | Get Instagram post stats including the share count | 5 (advanced) |
| `/v1/instagram/tagged` | List posts an Instagram user is tagged in | 5 (advanced) |
| `/v1/instagram/location/posts` | List recent posts at an Instagram location | 5 (advanced) |
| `/v1/instagram/engagement` | Get Instagram engagement statistics | 5 (advanced) |
| `/v1/instagram/search/location` | Search Instagram locations | 5 (advanced) |
| `/v1/instagram/username-suggestions` | Get Instagram username suggestions | 5 (advanced) |
| `/v1/instagram/search/music` | Search Instagram music | 5 (advanced) |
| `/v1/instagram/stories` | List an Instagram user's active stories | 5 (advanced) |
| `/v1/instagram/story/download` | Download a single Instagram story | 5 (advanced) |
| `/v1/instagram/music/trending` | List trending Instagram music | 5 (advanced) |
| `/v1/instagram/profile/full` | Instagram profile, recent posts, and computed analytics in one call. | 5 (custom) |
| `/v1/instagram/profile/reels/full` | Instagram reels with views, likes, comments, and per-reel share counts where available, in one call. | 5 (advanced) |
| `/v1/instagram/profile/posts/full` | Instagram posts with views, likes, comments, and per-post share counts where available, in one call. | 5 (advanced) |

### Kick (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/kick/clip` | Get Kick clip details | 1 (standard) |

### Komi (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/komi/page` | Get Komi page | 1 (standard) |

### Kwai (3)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/kwai/profile` | Get a Kwai user profile | 1 (standard) |
| `/v1/kwai/user/posts` | List a Kwai user's posts | 1 (standard) |
| `/v1/kwai/post` | Get a Kwai post | 1 (standard) |

### Linkbio (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/linkbio/page` | Get Linkbio page | 1 (standard) |

### LinkedIn (44)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/linkedin/profile` | Get LinkedIn user profile | 5 (advanced) |
| `/v1/linkedin/company` | Get LinkedIn company page | 5 (advanced) |
| `/v1/linkedin/post` | Get LinkedIn post details | 5 (advanced) |
| `/v1/linkedin/search/people` | Search LinkedIn people | 10 (premium) |
| `/v1/linkedin/company/people` | List people at a LinkedIn company | 10 (premium) |
| `/v1/linkedin/post/comments` | Get LinkedIn post comments | 5 (advanced) |
| `/v1/linkedin/profile/posts` | List a LinkedIn member's posts | 5 (advanced) |
| `/v1/linkedin/profile/reactions` | List posts a LinkedIn member reacted to | 5 (advanced) |
| `/v1/linkedin/post/reposts` | List reposts of a LinkedIn post | 5 (advanced) |
| `/v1/linkedin/group/posts` | List posts in a LinkedIn group | 5 (advanced) |
| `/v1/linkedin/company/affiliated-pages` | List a company's affiliated/showcase pages | 5 (advanced) |
| `/v1/linkedin/post/comments/replies` | List replies to a LinkedIn comment | 5 (advanced) |
| `/v1/linkedin/profile/experiences` | List a member's work experiences | 5 (advanced) |
| `/v1/linkedin/profile/educations` | List a member's education history | 5 (advanced) |
| `/v1/linkedin/profile/skills` | List a member's skills | 5 (advanced) |
| `/v1/linkedin/profile/honors` | List a member's honors and awards | 5 (advanced) |
| `/v1/linkedin/profile/certifications` | List a member's licenses and certifications | 5 (advanced) |
| `/v1/linkedin/profile/publications` | List a member's publications | 5 (advanced) |
| `/v1/linkedin/profile/volunteers` | List a member's volunteer experiences | 5 (advanced) |
| `/v1/linkedin/profile/recommendations` | List recommendations for a member | 5 (advanced) |
| `/v1/linkedin/profile/interests/companies` | List companies a member follows | 5 (advanced) |
| `/v1/linkedin/profile/interests/groups` | List groups a member follows | 5 (advanced) |
| `/v1/linkedin/profile/images` | List a member's image posts | 5 (advanced) |
| `/v1/linkedin/profile/videos` | List a member's video posts | 5 (advanced) |
| `/v1/linkedin/profile/comments` | List a member's comments | 5 (advanced) |
| `/v1/linkedin/post/reactions` | List reactors on a LinkedIn post | 10 (premium) |
| `/v1/linkedin/company/jobs` | List a company's job postings | 10 (premium) |
| `/v1/linkedin/search/jobs` | Search LinkedIn jobs | 10 (premium) |
| `/v1/linkedin/search/location` | Resolve a location to a LinkedIn geocode id | 1 (standard) |
| `/v1/linkedin/search/schools` | Search LinkedIn schools | 1 (standard) |
| `/v1/linkedin/search/industry` | Resolve an industry name to a LinkedIn industry id | 1 (standard) |
| `/v1/linkedin/profile/about` | Get a member's profile metadata (joined date, freshness) | 5 (advanced) |
| `/v1/linkedin/profile/contact` | Get a member's public contact info | 5 (advanced) |
| `/v1/linkedin/profile/stats` | Get a member's follower + connection counts | 5 (advanced) |
| `/v1/linkedin/company/job-count` | Get a company's open job count | 5 (advanced) |
| `/v1/linkedin/company/insights` | Get aggregate insights about a company's members | 5 (advanced) |
| `/v1/linkedin/group` | Get LinkedIn group details | 5 (advanced) |
| `/v1/linkedin/job` | Get LinkedIn job details | 5 (advanced) |
| `/v1/linkedin/company/posts` | List LinkedIn company posts | 5 (advanced) |
| `/v1/linkedin/ad` | Get LinkedIn ad details | 5 (advanced) |
| `/v1/linkedin/ads/search` | Search LinkedIn ads | 5 (advanced) |
| `/v1/linkedin/search/posts` | Search public LinkedIn posts by keyword | 5 (advanced) |
| `/v1/linkedin/post/transcript` | Get a LinkedIn post video transcript | 10 (premium) |
| `/v1/linkedin/profile/full` | LinkedIn company profile, recent posts, and computed analytics in one call. | 5 (custom) |

### Linkme (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/linkme/page` | Get Linkme profile | 1 (standard) |

### Linktree (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/linktree/page` | Get Linktree page | 1 (standard) |

### Naver (12)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/naver/blog/search` | Search Naver Blog | 1 (standard) |
| `/v1/naver/news/search` | Search Naver News | 1 (standard) |
| `/v1/naver/book/search` | Search Naver Book | 1 (standard) |
| `/v1/naver/encyc/search` | Search Naver Encyclopedia | 1 (standard) |
| `/v1/naver/cafearticle/search` | Search Naver Cafe articles | 1 (standard) |
| `/v1/naver/kin/search` | Search Naver KnowledgeiN (지식iN) | 1 (standard) |
| `/v1/naver/local/search` | Search Naver Local (장소 검색) | 1 (standard) |
| `/v1/naver/shop/search` | Search Naver Shopping | 1 (standard) |
| `/v1/naver/doc/search` | Search Naver Academic Documents (전문자료) | 1 (standard) |
| `/v1/naver/image/search` | Search Naver Image | 1 (standard) |
| `/v1/naver/webkr/search` | Search Naver Web (웹문서) | 1 (standard) |
| `/v1/naver/brief` | One query across the Korean internet (6 Naver corpora) + optional digest. | 10 (custom) |

### Perplexity (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/perplexity/research` | Web research via Perplexity Sonar | 1 (standard) |

### Pillar (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/pillar/page` | Get Pillar page | 1 (standard) |

### Pinterest (5)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/pinterest/search` | Search Pinterest pins | 1 (standard) |
| `/v1/pinterest/pin` | Get Pinterest pin details | 1 (standard) |
| `/v1/pinterest/url-stats` | Get Pinterest save counts for external URLs | 1 (standard) |
| `/v1/pinterest/board` | Get Pinterest board | 1 (standard) |
| `/v1/pinterest/user/boards` | List Pinterest user boards | 1 (standard) |

### Polymarket (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/polymarket/research` | Polymarket prediction markets — multi-query research | 5 (advanced) |

### Prism (33)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/prism/lookup` | Universal URL dispatcher: any social/commerce URL → the right detail endpoint's unified response. | 0 (custom) |
| `/v1/prism/comments` | Every comment on a post, replies nested, server-paginated to completion. | 1 (standard) |
| `/v1/prism/brand-mentions` | Brand mention volume time-series, sentiment split, top sources, and recent mentions for one keyword. | 50 (custom) |
| `/v1/prism/demand-signals` | Consumer-demand nowcast: app-review velocity, web mention slope, Reddit velocity, and commerce review levels, fused into a published demand index. | 30 (custom) |
| `/v1/prism/campaign` | Campaign tracker: pre/during/post volume lift, cross-platform engagement, and ranked top amplifiers for a hashtag or phrase. | 35 (custom) |
| `/v1/prism/ai-visibility` | AI Share-of-Voice / GEO monitoring: prompt set x reruns to per-brand appearance-% per AI engine plus a cited-domain ranking. | 2 (custom) |
| `/v1/prism/crisis-postmortem` | Crisis post-mortem: a who-said-what-first timeline across web, Reddit, Hacker News, and social, with an origin, peak, propagation sequence, and a grounded narrative. | 35 (custom) |
| `/v1/prism/crisis-radar` | Stateless crisis breach check: a z-score on daily mention volume and negative share, with on-breach confirmation and a severity grade. | 15 (custom) |
| `/v1/prism/devtool-pulse` | Developer-brand health: a devtool's repo dossier + Hacker News reaction + Reddit chatter + dev-blog echo, in one call. | 20 (custom) |
| `/v1/prism/leads` | Ranked feed of public conversations where people seek alternatives to or are switching from a competitor. | 50 (custom) |
| `/v1/prism/earned-media` | A brand's earned-media footprint — news + tech-press + fresh-web clips, deduped and ranked, with an outlet-coverage rollup. | 25 (custom) |
| `/v1/prism/truthsocial-pulse` | A Truth Social handle's pulse — profile, recent posts, per-post detail drill, and the news echo, in one call. | 20 (custom) |
| `/v1/prism/launch-echo` | How a launch landed — the Hacker News reaction (top threads + comments), the dev-blog echo, and an optional repo dossier. | 20 (custom) |
| `/v1/prism/audience-overlap` | How much two TikTok creators' commenter audiences overlap — Jaccard, shared-fan count, and a confidence label. | 20 (custom) |
| `/v1/prism/reputation` | A brand's cross-source reputation — Trustpilot + app stores + Google Business + web sentiment, blended into one weighted score with themed pros/cons. | 30 (custom) |
| `/v1/prism/employer-brand` | A company's employer brand — what people say about working there across Reddit, the web, YouTube, Naver, and the company's own LinkedIn voice. | 30 (custom) |
| `/v1/prism/audience-questions` | The real questions a topic's audience asks — harvested from Reddit + YouTube threads and clustered by intent (who/what/why/how/vs). | 30 (custom) |
| `/v1/prism/product-reviews` | A product's reviews across Amazon + Google Shopping + Trustpilot, folded into a cross-marketplace rating + themed pros/cons report. | 30 (custom) |
| `/v1/prism/apps-lookup` | One app across Google Play + the App Store — resolved, title-matched, and compared into a cross-store rating + listing report. | 30 (custom) |
| `/v1/prism/org-radar` | A GitHub org's footprint — its top repos each expanded into a full dossier (releases, issue load, top request/complaint), rolled up. | 26 (custom) |
| `/v1/prism/creator-vet` | Vet a creator before partnering — engagement quality, commenter authenticity, posting cadence, and controversy signals, optionally across platforms. | 50 (custom) |
| `/v1/prism/korea-gap` | What the world is talking about that Korea isn't (and vice versa) — the global vs Korean (Naver) conversation gap for a brand/topic. | 40 (custom) |
| `/v1/prism/share-of-voice` | Engagement-weighted Share of Voice across 2-5 brands, with web+social split, emotion overlay, and ESOV. | 40 (custom) |
| `/v1/prism/review-integrity` | Cross-source review integrity verdict (statistical, deterministic). | 30 (custom) |
| `/v1/prism/answers` | Multi-engine AI consensus: one question → Perplexity + Grok + Tavily answers verbatim, merged citations, and an agreement matrix. | 15 (custom) |
| `/v1/prism/video-intel` | One video URL → detail + stats + transcript + top comments + commenter sample, across YouTube/TikTok/Rumble/Instagram. | 5 (custom) |
| `/v1/prism/voice` | One person's public posts across X, Threads, Bluesky, and Truth Social, time-merged. | 5 (custom) |
| `/v1/prism/app-reviews` | Cross-store app review intelligence (Google Play + App Store) — translated, clustered, sentiment-scored. | 15 (custom) |
| `/v1/prism/creator-card` | One handle, unified author cards across TikTok, Instagram, YouTube, X (and more). | 5 (custom) |
| `/v1/prism/handle-audit` | Should you pull this handle? One call scores a handle across platforms, ranks the best ones, and projects the data volume + credit cost to pull it. | 5 (custom) |
| `/v1/prism/post-stats` | Up to 100 mixed-platform post URLs → current engagement per URL, failed URLs refunded. | 1 (custom) |
| `/v1/prism/comment-lookup` | Re-check up to 25 known comments in one call — per-item results, failed items refunded. | 2 (custom) |
| `/v1/prism/profiles` | Up to 50 (platform, handle) pairs → one canonical Author per row, failed handles refunded. | 1 (custom) |

### Reddit (7)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/reddit/subreddit` | List Reddit subreddit posts | 1 (standard) |
| `/v1/reddit/subreddit/details` | Get Reddit subreddit details | 1 (standard) |
| `/v1/reddit/search` | Search Reddit posts | 1 (standard) |
| `/v1/reddit/post/comments` | List Reddit post comments | 5 (advanced) |
| `/v1/reddit/subreddit/search` | Search within a subreddit | 1 (standard) |
| `/v1/reddit/post/transcript` | Get a Reddit video post transcript | 10 (premium) |
| `/v1/reddit/omni-search` | Reddit VoC sweep: one keyword → threads across all of Reddit with subreddit attribution and top comments inline. | 1 (standard) |

### Rumble (5)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/rumble/search` | Search Rumble videos | 1 (standard) |
| `/v1/rumble/channel/videos` | List videos for a Rumble channel | 1 (standard) |
| `/v1/rumble/video` | Get a Rumble video | 1 (standard) |
| `/v1/rumble/video/transcript` | Get a Rumble video transcript | 10 (premium) |
| `/v1/rumble/video/comments` | List top-level comments on a Rumble video | 1 (standard) |

### Snapchat (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/snapchat/profile` | Get Snapchat user profile | 1 (standard) |

### Spotify (6)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/spotify/artist` | Get a Spotify artist | 1 (standard) |
| `/v1/spotify/track` | Get a Spotify track | 1 (standard) |
| `/v1/spotify/album` | Get a Spotify album | 1 (standard) |
| `/v1/spotify/search` | Search Spotify | 1 (standard) |
| `/v1/spotify/podcast` | Get a Spotify podcast | 1 (standard) |
| `/v1/spotify/podcast/episodes` | List a Spotify podcast's episodes | 1 (standard) |

### Tavily (4)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/tavily/search` | Tavily web search with optional LLM-generated answer | 1 (standard) |
| `/v1/tavily/extract` | Extract clean content from one or more URLs | 1 (standard) |
| `/v1/tavily/map` | Map a website's sitegraph | 1 (standard) |
| `/v1/tavily/crawl` | Crawl a website with LLM-driven path selection | 1 (standard) |

### Threads (5)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/threads/profile` | Get Threads user profile | 1 (standard) |
| `/v1/threads/user/posts` | List Threads user posts | 1 (standard) |
| `/v1/threads/post` | Get Threads post details | 1 (standard) |
| `/v1/threads/search` | Search Threads posts | 1 (standard) |
| `/v1/threads/search/users` | Search Threads users | 1 (standard) |

### TikTok (20)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/tiktok/profile` | Get TikTok user profile | 1 (standard) |
| `/v1/tiktok/profile/videos` | List TikTok user videos | 1 (standard) |
| `/v1/tiktok/post` | Get TikTok post details | 1 (standard) |
| `/v1/tiktok/post/comments` | List TikTok post comments | 1 (standard) |
| `/v1/tiktok/video/comment/replies` | List TikTok comment replies | 1 (standard) |
| `/v1/tiktok/comment` | Look up one TikTok comment by URL or id | 2 (custom) |
| `/v1/tiktok/search` | Search TikTok videos by keyword | 1 (standard) |
| `/v1/tiktok/trending` | Get TikTok trending feed | 5 (advanced) |
| `/v1/tiktok/search/hashtag` | Search TikTok by hashtag | 1 (standard) |
| `/v1/tiktok/search/top` | TikTok top search results | 1 (standard) |
| `/v1/tiktok/search/users` | Search TikTok users | 1 (standard) |
| `/v1/tiktok/user/audience` | Get TikTok user audience demographics | 5 (advanced) |
| `/v1/tiktok/user/followers` | List TikTok user followers | 1 (standard) |
| `/v1/tiktok/user/following` | List TikTok user following | 1 (standard) |
| `/v1/tiktok/user/live` | Get TikTok user live stream | 1 (standard) |
| `/v1/tiktok/post/transcript` | Get TikTok video transcript | 10 (premium) |
| `/v1/tiktok/song` | Get TikTok song details | 1 (standard) |
| `/v1/tiktok/song/videos` | List TikTok videos using a song | 1 (standard) |
| `/v1/tiktok/profile/region` | Get TikTok profile region | 1 (standard) |
| `/v1/tiktok/profile/full` | TikTok profile, recent posts, and computed analytics in one call. | 5 (custom) |

### TikTok Shop (5)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/tiktokshop/product` | Get TikTok Shop product details | 1 (standard) |
| `/v1/tiktokshop/product/reviews` | List TikTok Shop product reviews | 1 (standard) |
| `/v1/tiktokshop/products` | List TikTok Shop products | 1 (standard) |
| `/v1/tiktokshop/search` | Search TikTok Shop products | 1 (standard) |
| `/v1/tiktokshop/user/showcase` | List TikTok user showcase products | 1 (standard) |

### Tripadvisor (2)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/tripadvisor/search` | Search TripAdvisor businesses & places | 1 (standard) |
| `/v1/tripadvisor/reviews` | Get TripAdvisor reviews for a place | 1 (standard) |

### Trustpilot (2)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/trustpilot/business-search` | Search Trustpilot businesses | 1 (standard) |
| `/v1/trustpilot/reviews` | Get Trustpilot reviews for a business | 5 (advanced) |

### Truth Social (3)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/truthsocial/profile` | Get Truth Social user profile | 1 (standard) |
| `/v1/truthsocial/user/posts` | List Truth Social user posts | 1 (standard) |
| `/v1/truthsocial/post` | Get Truth Social post details | 1 (standard) |

### Twitch (4)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/twitch/profile` | Get Twitch streamer profile | 1 (standard) |
| `/v1/twitch/clip` | Get Twitch clip details | 1 (standard) |
| `/v1/twitch/user/videos` | List a Twitch user's videos | 1 (standard) |
| `/v1/twitch/user/schedule` | Get a Twitch user's stream schedule | 1 (standard) |

### Twitter/X (8)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/twitter/profile` | Get Twitter user profile | 1 (standard) |
| `/v1/twitter/user/tweets` | List Twitter user tweets | 1 (standard) |
| `/v1/twitter/tweet` | Get Twitter tweet details | 1 (standard) |
| `/v1/twitter/community` | Get Twitter community details | 1 (standard) |
| `/v1/twitter/community/tweets` | List Twitter community tweets | 1 (standard) |
| `/v1/twitter/tweet/transcript` | Get Twitter video transcript | 10 (premium) |
| `/v1/twitter/ai-search` | AI-powered X (Twitter) search via xAI Grok | 5 (advanced) |
| `/v1/twitter/profile/full` | X (Twitter) profile, recent posts, and computed analytics in one call. | 5 (custom) |

### Universal Search (2)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/search/everywhere` | Universal social search across 12 platforms | 20 (custom) |
| `/v1/search/forums` | Fused forum search across Reddit, Hacker News, and Naver 지식iN/카페 — with top comments inline on hero threads by default. | 10 (custom) |

### Utility (1)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/utility/age-gender` | Detect age and gender | 10 (premium) |

### Web (22)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/web/scrape` | Scrape a web page | 1 (custom) |
| `/v1/web/search` | Search the web | 2 (custom) |
| `/v1/web/map` | Map URLs on a site | 1 (custom) |
| `/v1/web/extract` | Extract structured data from a web page | 5 (custom) |
| `/v1/web/crawl` | Start an async web crawl | 1 (custom) |
| `/v1/web/batch-scrape` | Start an async batch scrape | 1 (custom) |
| `/v1/web/jobs` | List async web jobs | 0 (custom) |
| `/v1/web/jobs/{job_id}` | Get an async web job | 0 (custom) |
| `/v1/web/jobs/{job_id}` | Cancel an async web job | 0 (custom) |
| `/v1/web/agent` | Start an async web agent job | 25 (custom) |
| `/v1/web/monitors` | Create a web monitor | 0 (custom) |
| `/v1/web/monitors` | List web monitors | 0 (custom) |
| `/v1/web/monitors/{monitor_id}` | Get a web monitor | 0 (custom) |
| `/v1/web/monitors/{monitor_id}` | Update a web monitor | 0 (custom) |
| `/v1/web/monitors/{monitor_id}` | Delete a web monitor | 0 (custom) |
| `/v1/web/monitors/{monitor_id}/checks` | List web monitor checks | 0 (custom) |
| `/v1/web/sessions` | Create an interactive web session | 5 (custom) |
| `/v1/web/sessions` | List interactive web sessions | 0 (custom) |
| `/v1/web/sessions/{session_id}` | Get an interactive web session | 0 (custom) |
| `/v1/web/sessions/{session_id}/execute` | Execute an interaction in a web session | 0 (custom) |
| `/v1/web/sessions/{session_id}` | Close an interactive web session | 0 (custom) |
| `/v1/web/parse` | Parse an uploaded document | 1 (custom) |

### YouTube (28)

| Endpoint | What it returns | Credits |
|----------|-----------------|--------|
| `/v1/youtube/channel` | Get YouTube channel info | 1 (standard) |
| `/v1/youtube/channel/videos` | List YouTube channel videos | 1 (standard) |
| `/v1/youtube/video` | Get YouTube video details | 1 (standard) |
| `/v1/youtube/videos` | Batch get YouTube video details (up to 1000) | 5 (advanced) |
| `/v1/youtube/channels` | Batch get YouTube channel details (up to 1000) | 5 (advanced) |
| `/v1/youtube/transcripts` | Up to 100 YouTube video ids → one transcript per row, failed ids refunded. | 3 (custom) |
| `/v1/youtube/video/sponsors` | Detect sponsors of a YouTube video | 10 (premium) |
| `/v1/youtube/video/comments` | List YouTube video comments | 1 (standard) |
| `/v1/youtube/video/comment/replies` | List YouTube comment replies | 1 (standard) |
| `/v1/youtube/search` | Search YouTube | 1 (standard) |
| `/v1/youtube/channel/shorts` | List YouTube channel shorts | 1 (standard) |
| `/v1/youtube/community-post` | Get YouTube community post | 1 (standard) |
| `/v1/youtube/playlist` | Get YouTube playlist | 1 (standard) |
| `/v1/youtube/search/hashtag` | Search YouTube by hashtag | 1 (standard) |
| `/v1/youtube/shorts/trending` | Get trending YouTube shorts | 5 (advanced) |
| `/v1/youtube/video/transcript` | Get YouTube video transcript | 3 (custom) |
| `/v1/youtube/channel/playlists` | List a YouTube channel's playlists | 1 (standard) |
| `/v1/youtube/channel/lives` | List a YouTube channel's live streams | 1 (standard) |
| `/v1/youtube/channel/community-posts` | List a YouTube channel's community posts | 1 (standard) |
| `/v1/youtube/videos/trending` | Get trending YouTube videos | 1 (standard) |
| `/v1/youtube/playlist/items` | List the videos in a YouTube playlist | 1 (standard) |
| `/v1/youtube/search/advanced` | Advanced YouTube video search | 1 (standard) |
| `/v1/youtube/search/suggestions` | Get YouTube search suggestions | 1 (standard) |
| `/v1/youtube/video/audio` | Get a YouTube video's audio file streams | 5 (advanced) |
| `/v1/youtube/video/files` | Get a YouTube video's video file streams | 5 (advanced) |
| `/v1/youtube/video/subtitles` | Get a YouTube video's subtitle files | 1 (standard) |
| `/v1/youtube/video/thumbnails` | Get a YouTube video's thumbnail files | 1 (standard) |
| `/v1/youtube/profile/full` | YouTube profile, recent posts, and computed analytics in one call. | 5 (custom) |
