# Twitter/X

8 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 5 standard (1 credit), 1 advanced (5), 1 premium (10), 1 custom (flat/metered) — the exact cost is in each endpoint heading below.

## GET /v1/twitter/profile — 1 credit (standard)

Get Twitter user profile

- `handle` (required) — Twitter username without the @ symbol

```bash
curl "https://www.socialcrawl.dev/v1/twitter/profile?handle=elonmusk" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitter/user/tweets — 1 credit (standard)

List Twitter user tweets

- `handle` (required) — Twitter username without the @ symbol
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/twitter/user/tweets?handle=elonmusk" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitter/tweet — 1 credit (standard)

Get Twitter tweet details

- `url` (required) — Full URL of the tweet
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/twitter/tweet?url=https://x.com/elonmusk/status/1234567890" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitter/community — 1 credit (standard)

Get Twitter community details

- `url` (required) — Full URL of the Twitter/X community

```bash
curl "https://www.socialcrawl.dev/v1/twitter/community?url=https://x.com/i/communities/1926186499399139650" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitter/community/tweets — 1 credit (standard)

List Twitter community tweets

- `url` (required) — Full URL of the Twitter/X community

```bash
curl "https://www.socialcrawl.dev/v1/twitter/community/tweets?url=https://x.com/i/communities/1234567890" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitter/tweet/transcript — 10 credits (premium)

Get Twitter video transcript

- `url` (required) — Full URL of the tweet containing a video

```bash
curl "https://www.socialcrawl.dev/v1/twitter/tweet/transcript?url=https://x.com/TheoVon/status/1916982720317821050" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitter/ai-search — 5 credits (advanced)

AI-powered X (Twitter) search via xAI Grok

- `query` (required) — Natural-language prompt describing what you want to learn from X. The model autonomously searches X using the x_search tool with any handle / date filters you provide.
- `from_handles` (optional, string) — Comma-separated X handles (max 10). Restricts the search to posts from these accounts only. Mutually exclusive with exclude_handles.
- `exclude_handles` (optional, string) — Comma-separated X handles (max 10) to exclude from search results. Mutually exclusive with from_handles.
- `from_date` (optional, string) — ISO 8601 start date (YYYY-MM-DD). Limits the search window to posts on or after this date.
- `to_date` (optional, string) — ISO 8601 end date (YYYY-MM-DD). Limits the search window to posts on or before this date.

```bash
curl "https://www.socialcrawl.dev/v1/twitter/ai-search?query=What is @elonmusk saying about xAI this week?" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitter/profile/full — 5 credits (custom)

X (Twitter) profile, recent posts, and computed analytics in one call.

- `handle` (optional, string)
- `posts` (optional, integer) — How many recent posts to fetch + average the computed metrics over (1–100, default 25).
- `cursor` (optional, string) — Pass a prior response's posts_cursor to deepen the post window.
- `include` (optional, string) — CSV subset of posts,computed (default both). include=computed drops the raw posts[] to save payload.

```bash
curl "https://www.socialcrawl.dev/v1/twitter/profile/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
