# TikTok

20 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 15 standard (1 credit), 2 advanced (5), 1 premium (10), 2 custom (flat/metered) — the exact cost is in each endpoint heading below.

## GET /v1/tiktok/profile — 1 credit (standard)

Get TikTok user profile

- `handle` (optional, string) — TikTok username without the @ symbol.
- `user_id` (optional, string) — TikTok numeric user ID. Use this for faster responses.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/profile" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/profile/videos — 1 credit (standard)

List TikTok user videos

- `handle` (required) — TikTok username without the @ symbol
- `user_id` (optional, string) — TikTok user id. Use this for faster responses.
- `sort_by` (optional, enum: latest | popular) — What to sort by
- `max_cursor` (optional, string) — Cursor to get more videos. Get 'max_cursor' from previous response.
- `region` (optional, string) — Region (Country) you want the proxy in. Defaults to US.
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/profile/videos?handle=charlidamelio" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/post — 1 credit (standard)

Get TikTok post details

- `url` (required) — Full URL of the TikTok video
- `region` (optional, string) — Region of the proxy. Sometimes you'll need to specify the region if you're not getting a response. Commonly for videos from the Phillipines, in which case you'd use 'PH'. Use 2 letter country codes like US, GB, FR, etc
- `trim` (optional, boolean) — Set to true to get a trimmed response
- `download_media` (optional, boolean) — Set to true to also download the video/images and get back permanent, durable media URLs under `data.post.ext.download_media_urls` (`[{ post_id, cdn_url, type, cached }]`). Use these for archiving — the raw `media_urls` are short-lived signed CDN links that expire. Adds a few seconds of latency while the media is fetched.

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/post?url=https://www.tiktok.com/@charlidamelio/video/7321485815660738859" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/post/comments — 1 credit (standard)

List TikTok post comments

- `url` (required) — Full URL of the TikTok video to fetch comments for
- `cursor` (optional, integer) — Cursor to get more comments. Get 'cursor' from previous response.
- `trim` (optional, boolean) — Set to true to get a trimmed response

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/post/comments?url=https://www.tiktok.com/@charlidamelio/video/7321485815660738859" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/video/comment/replies — 1 credit (standard)

List TikTok comment replies

- `comment_id` (required) — TikTok comment ID. This is the cid from the comments endpoint.
- `url` (required) — TikTok video URL. This is the url from the comments endpoint.
- `cursor` (optional, integer) — Cursor to get more replies. Get 'cursor' from previous response.

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/video/comment/replies?comment_id=7623828115408274207" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/comment — 2 credits (custom)

Look up one TikTok comment by URL or id

- `comment_url` (optional, string) — A TikTok comment URL: `https://www.tiktok.com/@{handle}/video/{videoId}?comment_id={cid}`, the `m.tiktok.com/v/{id}.html?...&share_comment_id={cid}` share form, or a `vm.tiktok.com/{code}` / `tiktok.com/t/{code}` shortlink. Mutually exclusive with `post_url`+`comment_id`.
- `post_url` (optional, string) — The post URL (`https://www.tiktok.com/@{handle}/video/{videoId}`). Combine with `comment_id`, or with `author_username`/`text_contains` for a search.
- `comment_id` (optional, string) — The target comment's numeric id (the `cid` from the comments endpoint). Requires `post_url`.
- `parent_comment_id` (optional, string) — The parent comment's numeric id — supply this when the target is a reply so it can be resolved directly via the native replies endpoint.
- `author_username` (optional, string) — Return up to `max` comments authored by this username (no comment id needed). Mutually exclusive with `text_contains` and any comment id.
- `text_contains` (optional, string) — Return up to `max` comments whose text contains this snippet (case-insensitive). Mutually exclusive with `author_username` and any comment id.
- `deep_scan` (optional, boolean) — Widen the scan budget for deeply-buried comments (raises the page ceiling and deadline). Bills 6 credits instead of 2.
- `position_hint` (optional, string) — Opaque token from a prior lookup's `lookup.position_hint`. Passing it back probes the comment's last-known location first, making a re-check of an already-found comment cheap.
- `max` (optional, integer) — For `author_username`/`text_contains` search: max matches to return (1–20, default 5).

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/comment" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/search — 1 credit (standard)

Search TikTok videos by keyword

- `query` (required) — Search keyword or phrase to find TikTok videos
- `date_posted` (optional, enum: yesterday | this-week | this-month | last-3-months | last-6-months | all-time) — Time Frame
- `sort_by` (optional, enum: relevance | most-liked | date-posted) — Sort by
- `region` (optional, string) — Note, this doesn't filter the tiktoks only in a specfic region, it puts the proxy there. Use it in case you want to scrape posts only available for some country. Use 2 letter country codes like US, GB, FR, etc
- `cursor` (optional, integer) — Cursor to get more videos. Get 'cursor' from previous response.
- `trim` (optional, boolean) — Set to true to get a trimmed response

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/search?query=cooking recipes" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/trending — 5 credits (advanced)

Get TikTok trending feed

- `region` (required) — ISO 3166-1 alpha-2 country code (e.g., US, GB, KR)
- `trim` (optional, boolean) — Set to true to get a trimmed response.

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/trending?region=US" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/search/hashtag — 1 credit (standard)

Search TikTok by hashtag

- `hashtag` (required) — Hashtag to search for without the # symbol
- `region` (optional, string) — Region the proxy will be set to. Note: this isn't going to grab you all tiktoks from this region, you're just setting the proxy there.
- `cursor` (optional, integer) — Cursor to get more videos. Get 'cursor' from previous response.
- `trim` (optional, boolean) — Set to true to get a trimmed response

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/search/hashtag?hashtag=fyp" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/search/top — 1 credit (standard)

TikTok top search results

- `query` (required) — Search keyword or phrase
- `publish_time` (optional, enum: yesterday | this-week | this-month | last-3-months | last-6-months | all-time) — Time Frame TikTok was posted
- `sort_by` (optional, enum: relevance | most-liked | date-posted) — Sort by
- `region` (optional, string) — Note, this doesn't filter the tiktoks only in a specfic region, it puts the proxy there. Use it in case you want to scrape posts only available for some country. Use 2 letter country codes like US, GB, FR, etc
- `cursor` (optional, integer) — Cursor to get more videos. Get 'cursor' from previous response.

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/search/top?query=dance challenge" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/search/users — 1 credit (standard)

Search TikTok users

- `query` (required) — Search keyword or phrase to find TikTok users
- `cursor` (optional, integer) — Cursor to get more users. Get 'cursor' from previous response.
- `trim` (optional, boolean) — Set to true to get a trimmed response

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/search/users?query=cooking" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/user/audience — 5 credits (advanced)

Get TikTok user audience demographics

- `handle` (required) — TikTok username without the @ symbol

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/user/audience?handle=charlidamelio" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/user/followers — 1 credit (standard)

List TikTok user followers

- `handle` (optional, string) — TikTok username without the @ symbol
- `user_id` (optional, string) — User id. Use this for faster response times.
- `min_time` (optional, integer) — Used to paginate. Get 'min_time' from previous response.
- `trim` (optional, boolean) — Set to true to get a trimmed response

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/user/followers" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/user/following — 1 credit (standard)

List TikTok user following

- `handle` (required) — TikTok username without the @ symbol
- `trim` (optional, boolean) — Set to true to get a trimmed response

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/user/following?handle=stoolpresidente" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/user/live — 1 credit (standard)

Get TikTok user live stream

- `handle` (required) — TikTok username without the @ symbol

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/user/live?handle=charlidamelio" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/post/transcript — 10 credits (premium)

Get TikTok video transcript

- `url` (required) — Full URL of the TikTok video
- `language` (optional, string) — Language of the transcript. 2 letter language code, ie 'en', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh'
- `use_ai_as_fallback` (optional, string) — Set to 'true' to use AI as a fallback to get the transcript if the transcript is not found. Costs 10 credits to use this feature. And only if the video is under 2 minutes.

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/post/transcript?url=https://www.tiktok.com/@stoolpresidente/video/7499229683859426602" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/song — 1 credit (standard)

Get TikTok song details

- `clipId` (required) — TikTok sound/song clip ID

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/song?clipId=7439295283975702544" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/song/videos — 1 credit (standard)

List TikTok videos using a song

- `clipId` (optional, string) — TikTok sound/song clip ID
- `cursor` (optional, integer) — The cursor to get the next page of results.

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/song/videos" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/profile/region — 1 credit (standard)

Get TikTok profile region

- `handle` (required) — TikTok username without the @ symbol

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/profile/region?handle=stoolpresidente" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/tiktok/profile/full — 5 credits (custom)

TikTok profile, recent posts, and computed analytics in one call.

- `handle` (optional, string)
- `user_id` (optional, string)
- `posts` (optional, integer) — How many recent posts to fetch + average the computed metrics over (1–100, default 25).
- `cursor` (optional, string) — Pass a prior response's posts_cursor to deepen the post window.
- `include` (optional, string) — CSV subset of posts,computed (default both). include=computed drops the raw posts[] to save payload.

```bash
curl "https://www.socialcrawl.dev/v1/tiktok/profile/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
