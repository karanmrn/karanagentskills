# Facebook

22 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 15 standard (1 credit), 4 advanced (5), 2 premium (10), 1 custom (flat/metered) — the exact cost is in each endpoint heading below.

## GET /v1/facebook/profile — 1 credit (standard)

Get Facebook page profile

- `url` (required) — Full URL of the Facebook page or profile
- `get_business_hours` (optional, string) — Get the business's hours

```bash
curl "https://www.socialcrawl.dev/v1/facebook/profile?url=https://www.facebook.com/Meta" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/profile/posts — 1 credit (standard)

List Facebook page posts

- `url` (optional, string) — Full URL of the Facebook page or profile to fetch posts for
- `pageId` (optional, string) — Facebook profile page id
- `cursor` (optional, string) — To paginate through the posts

**At least one of `url` / `pageId` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/profile/posts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/post — 1 credit (standard)

Get Facebook post details

- `url` (required) — Full URL of the Facebook post
- `get_comments` (optional, boolean) — Whether you want to get the first several comments of the post
- `get_transcript` (optional, boolean) — Whether you want to get the transcript of the post

```bash
curl "https://www.socialcrawl.dev/v1/facebook/post?url=https://www.facebook.com/Meta/posts/1234567890" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/post/comments — 1 credit (standard)

List Facebook post comments

- `url` (optional, string) — Full URL of the Facebook post to fetch comments for
- `feedback_id` (optional, string) — Using feedback_id (instead of url) will *really* speed up the request. You can get the feedback_id when you make a request to /v1/facebook/post.
- `cursor` (optional, string) — Cursor to get more comments. Get 'cursor' from previous response.

**At least one of `url` / `feedback_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/post/comments" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/group/posts — 1 credit (standard)

List Facebook group posts

- `url` (optional, string) — Full URL of the Facebook group
- `group_id` (optional, string) — The ID of the group
- `sort_by` (optional, enum: TOP_POSTS | RECENT_ACTIVITY | CHRONOLOGICAL | CHRONOLOGICAL_LISTINGS) — How to sort the posts

**At least one of `url` / `group_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/group/posts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/post/transcript — 10 credits (premium)

Get Facebook video transcript

- `url` (required) — Full URL of the Facebook video post

```bash
curl "https://www.socialcrawl.dev/v1/facebook/post/transcript?url=https://www.facebook.com/Meta/videos/a-slightly-life-changing-story/1459847961114516/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/profile/photos — 1 credit (standard)

List Facebook profile photos

- `url` (required) — Full URL of the Facebook page or profile
- `next_page_id` (optional, string) — To paginate through to the next page
- `cursor` (optional, string) — To paginate through to the next page

```bash
curl "https://www.socialcrawl.dev/v1/facebook/profile/photos?url=https://www.facebook.com/Meta" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/profile/reels — 1 credit (standard)

List Facebook profile reels

- `url` (required) — Full URL of the Facebook page or profile
- `next_page_id` (optional, string) — To paginate through to the next page
- `cursor` (optional, string) — To paginate through to the next page

```bash
curl "https://www.socialcrawl.dev/v1/facebook/profile/reels?url=https://www.facebook.com/Meta" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/adlibrary/ad — 5 credits (advanced)

Get Facebook Ad Library ad details

- `id` (optional, string) — Facebook Ad Library ad ID
- `url` (optional, string) — Facebook Ad URL
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/adlibrary/ad" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/adlibrary/company/ads — 5 credits (advanced)

List Facebook Ad Library company ads

- `pageId` (optional, string) — Facebook page ID of the advertiser
- `companyName` (optional, string) — The name of the company. Can either use this or pageId
- `country` (optional, string) — This can only be one country. It has to be the 2 letter code for the country. It defaults to ALL.
- `status` (optional, enum: ALL | ACTIVE | INACTIVE) — Status of the ad. Defaults to ACTIVE.
- `media_type` (optional, enum: ALL | IMAGE | VIDEO | MEME | IMAGE_AND_MEME | NONE) — Media type of the ad. Defaults to ALL. Meme refers to ads with image and text. Not sure why they call it meme.
- `language` (optional, string) — Language to filter ads on. Needs to be 2 letter language code, ie EN, ES, FR, etc
- `sort_by` (optional, enum: total_impressions | relevancy_monthly_grouped) — Sort by impressions (high to low), or Most Recent (relevancy_monthly_grouped). Defaults to impressions.
- `start_date` (optional, string) — Start date to search for. Format: YYYY-MM-DD
- `end_date` (optional, string) — End date to search for. Format: YYYY-MM-DD
- `cursor` (optional, string) — Cursor to paginate through results
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

**At least one of `pageId` / `companyName` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/adlibrary/company/ads" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/adlibrary/search/ads — 5 credits (advanced)

Search Facebook Ad Library

- `query` (required) — Search keyword or phrase to find ads in the Facebook Ad Library
- `sort_by` (optional, enum: total_impressions | relevancy_monthly_grouped) — Sort by impressions (high to low), or Most Recent (relevancy_monthly_grouped). Defaults to impressions.
- `search_type` (optional, enum: keyword_unordered | keyword_exact_phrase) — If you want to search by exact phrase or not
- `ad_type` (optional, enum: all | political_and_issue_ads) — Search for all ads or only political and issue ads
- `country` (optional, string) — This can only be one country. It has to be the 2 letter code for the country. It defaults to ALL.
- `status` (optional, enum: ALL | ACTIVE | INACTIVE) — Status of the ad. Defaults to ACTIVE.
- `media_type` (optional, enum: ALL | IMAGE | VIDEO | MEME | IMAGE_AND_MEME | NONE) — Media type of the ad. Defaults to ALL. Meme just means the ad has text and an image. No clue why they call it meme.
- `start_date` (optional, string) — Impressions start date. Needs to be in YYYY-MM-DD format.
- `end_date` (optional, string) — Impressions end date. Needs to be in YYYY-MM-DD format.
- `cursor` (optional, string) — Cursor to paginate through results
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/facebook/adlibrary/search/ads?query=artificial intelligence" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/adlibrary/search/companies — 5 credits (advanced)

Search Facebook Ad Library companies

- `query` (required) — Search keyword or phrase to find companies in the Facebook Ad Library

```bash
curl "https://www.socialcrawl.dev/v1/facebook/adlibrary/search/companies?query=Nike" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/profile/events — 1 credit (standard)

List a Facebook page's events

- `url` (required) — Full URL of the public Facebook page.
- `cursor` (optional, string) — Cursor returned by the previous response for pagination.

```bash
curl "https://www.socialcrawl.dev/v1/facebook/profile/events?url=https://www.facebook.com/brickyardoldtown" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/post/comment/replies — 1 credit (standard)

List replies to a Facebook post comment

- `feedback_id` (required) — `feedback_id` from `/v1/facebook/post/comments` for the parent comment (this is NOT the comment ID).
- `expansion_token` (required) — `expansion_token` from `/v1/facebook/post/comments` for the parent comment.
- `cursor` (optional, string) — Cursor returned by the previous response for pagination.

```bash
curl "https://www.socialcrawl.dev/v1/facebook/post/comment/replies?feedback_id=ZmVlZGJhY2s6MzM3MzYxMzI5OTQ4Nzc1NV8xOTI5NTk0OTE3Njg3MTcz" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/marketplace/location/search — 1 credit (standard)

Search Facebook Marketplace locations

- `query` (required) — Location search query (city or area name).

```bash
curl "https://www.socialcrawl.dev/v1/facebook/marketplace/location/search?query=Los Angeles" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/marketplace/search — 1 credit (standard)

Search Facebook Marketplace listings

- `query` (required) — Search keyword (e.g., `bike`, `couch`).
- `lat` (required) — Latitude of the search location.
- `lng` (required) — Longitude of the search location.
- `radius_km` (optional, integer) — Search radius in kilometers.
- `min_price` (optional, integer) — Minimum listing price.
- `max_price` (optional, integer) — Maximum listing price.
- `count` (optional, integer) — Number of listings to return per page.
- `sort_by` (optional, enum: suggested | distance_ascend | creation_time_descend | price_ascend | price_descend) — Sort order for results.
- `delivery_method` (optional, enum: all | local_pickup | shipping) — Delivery filter — local pickup only, shipping only, or all.
- `condition` (optional, enum: new | used_like_new | used_good | used_fair) — Filter listings by item condition.
- `date_listed` (optional, enum: all | 1 | 7 | 30 | last_24_hours | last_7_days | last_30_days) — Filter by listing recency (relative window or numeric day count).
- `availability` (optional, enum: available | sold | all) — Filter by listing status — `available`, `sold`, or `all`.
- `cursor` (optional, string) — Opaque pagination cursor returned by the previous response — forward as-is.

```bash
curl "https://www.socialcrawl.dev/v1/facebook/marketplace/search?query=bike" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/marketplace/item — 1 credit (standard)

Get a Facebook Marketplace item

- `id` (optional, string) — Facebook Marketplace item ID (numeric).
- `url` (optional, string) — Full URL of the Marketplace item.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/marketplace/item" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/events/search — 1 credit (standard)

Search Facebook events by keyword

- `query` (required) — Event name or keyword to search for.
- `cursor` (optional, string) — Cursor returned by the previous response for pagination.

```bash
curl "https://www.socialcrawl.dev/v1/facebook/events/search?query=dogs" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/events — 1 credit (standard)

List Facebook events for a city

- `url` (required) — Full URL of the city's Facebook Events page.
- `time` (optional, enum: today | this_week | next_week) — Relative time window. Defaults to all time when omitted.
- `cursor` (optional, string) — Cursor returned by the previous response for pagination.

```bash
curl "https://www.socialcrawl.dev/v1/facebook/events?url=https://www.facebook.com/events/explore/saint-petersburg-florida/111326725552547" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/event/details — 1 credit (standard)

Get details for a Facebook event

- `id` (optional, string) — Facebook event ID (numeric).
- `url` (optional, string) — Full URL of the event.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/event/details" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/adlibrary/ad/transcript — 10 credits (premium)

Get a Facebook Ad Library video ad transcript

- `id` (optional, string) — Facebook Ad Library ad ID.
- `url` (optional, string) — Facebook Ad Library ad URL.

**At least one of `id` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/facebook/adlibrary/ad/transcript" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/facebook/profile/full — 5 credits (custom)

Facebook profile, recent posts, and computed analytics in one call.

- `url` (optional, string)
- `posts` (optional, integer) — How many recent posts to fetch + average the computed metrics over (1–100, default 25).
- `cursor` (optional, string) — Pass a prior response's posts_cursor to deepen the post window.
- `include` (optional, string) — CSV subset of posts,computed (default both). include=computed drops the raw posts[] to save payload.

```bash
curl "https://www.socialcrawl.dev/v1/facebook/profile/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
