# Instagram

33 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 11 standard (1 credit), 19 advanced (5), 1 premium (10), 2 custom (flat/metered) — the exact cost is in each endpoint heading below.

## GET /v1/instagram/profile — 1 credit (standard)

Get Instagram user profile

- `handle` (required) — Instagram username without the @ symbol
- `trim` (optional, boolean) — Set to true to get a trimmed response

```bash
curl "https://www.socialcrawl.dev/v1/instagram/profile?handle=instagram" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/profile/posts — 1 credit (standard)

List Instagram user posts

- `handle` (required) — Instagram username without the @ symbol
- `next_max_id` (optional, string) — Cursor to get next page of results.
- `trim` (optional, boolean) — Set to true to get a trimmed response

```bash
curl "https://www.socialcrawl.dev/v1/instagram/profile/posts?handle=instagram" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/post — 1 credit (standard)

Get Instagram post details

- `url` (required) — Full URL of the Instagram post
- `region` (optional, string) — 2 letter country code to set the proxy in
- `trim` (optional, boolean) — Set to true to get a trimmed response
- `download_media` (optional, boolean) — Set to true to also download the video/images and get back permanent, durable media URLs under `data.post.ext.download_media_urls` (`[{ post_id, cdn_url, type, cached }]`). Use these for archiving — the raw `media_urls` are short-lived signed CDN links that expire. Adds a few seconds of latency while the media is fetched.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/post?url=https://www.instagram.com/p/CwA1234abcd/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/post/comments — 5 credits (advanced)

List Instagram post comments

- `url` (required) — URL of the Instagram post (a /p/, /reel/, /reels/, or /tv/ link).
- `sort` (optional, enum: top | recent) — Ordering: `top` (default) ranks by Instagram's popularity order (most-liked first); `recent` returns newest-first.
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.
- `safe_url` (optional, boolean) — When true, returns URL-safe profile picture links suitable for embedding.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/post/comments?url=https://www.instagram.com/p/DXidPIVDU6M/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/comment — 5 credits (custom)

Look up one Instagram comment by URL or id

- `comment_url` (optional, string) — An Instagram comment permalink: `https://www.instagram.com/p/{shortcode}/c/{commentId}/` (or a reply permalink `.../c/{parent}/r/{reply}/`, best-effort). Mutually exclusive with `post_url`+`comment_id`.
- `post_url` (optional, string) — The post URL (a `/p/`, `/reel/`, `/reels/`, or `/tv/` link). Combine with `comment_id`, or with `author_username`/`text_contains` for a search.
- `comment_id` (optional, string) — The target comment's numeric id (`pk`). Requires `post_url`.
- `author_username` (optional, string) — Return up to `max` comments authored by this username (no comment id needed). Mutually exclusive with `text_contains` and any comment id.
- `text_contains` (optional, string) — Return up to `max` comments whose text contains this snippet (case-insensitive). Mutually exclusive with `author_username` and any comment id.
- `deep_scan` (optional, boolean) — Widen the scan budget for deeply-buried comments (raises the per-chain page ceiling and deadline). Bills 15 credits instead of 5.
- `position_hint` (optional, string) — Opaque token from a prior lookup's `lookup.position_hint`. Passing it back replays just the last-known sort chain first, making a re-check of an already-found comment cheap.
- `max` (optional, integer) — For `author_username`/`text_contains` search: max matches to return (1–20, default 5).

```bash
curl "https://www.socialcrawl.dev/v1/instagram/comment" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/basic-profile — 1 credit (standard)

Get Instagram basic profile

- `userId` (optional, string) — Instagram numeric user ID

```bash
curl "https://www.socialcrawl.dev/v1/instagram/basic-profile" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/profile/reels — 1 credit (standard)

List Instagram user reels

- `user_id` (optional, string) — Instagram user id. Use this for faster response times.
- `handle` (optional, string) — Instagram username without the @ symbol
- `max_id` (optional, string) — Max id to get more reels. Get 'max_id' from previous response.
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

**At least one of `user_id` / `handle` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/profile/reels" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/highlights — 1 credit (standard)

List Instagram story highlights

- `user_id` (optional, string) — Instagram user id. Use for faster response times.
- `handle` (optional, string) — Instagram username without the @ symbol

**At least one of `user_id` / `handle` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/highlights" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/highlight/detail — 1 credit (standard)

Get Instagram highlight detail

- `id` (optional, string) — Instagram highlight ID — the numeric id, with or without the `highlight:` prefix. Get it from `/v1/instagram/user/highlights`.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/highlight/detail" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/search/reels — 1 credit (standard)

Search Instagram reels

- `query` (required) — Search keyword or phrase to find Instagram reels
- `date_posted` (optional, enum: last-hour | last-day | last-week | last-month | last-year) — Date posted
- `page` (optional, integer) — The page number to return.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/search/reels?query=workout routine" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/media/transcript — 10 credits (premium)

Get Instagram media transcript

- `url` (required) — Full URL of the Instagram video or reel

```bash
curl "https://www.socialcrawl.dev/v1/instagram/media/transcript?url=https://www.instagram.com/reel/DHsD6HGqJhp/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/user/embed — 1 credit (standard)

Get Instagram user embed HTML

- `handle` (required) — Instagram username without the @ symbol

```bash
curl "https://www.socialcrawl.dev/v1/instagram/user/embed?handle=instagram" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/audio/reels — 1 credit (standard)

List Instagram reels using an audio track

- `audio_id` (required) — Instagram audio ID — the numeric id from an instagram.com/reels/audio/{audio_id}/ URL
- `cursor` (optional, string) — Pagination cursor from the previous response

```bash
curl "https://www.socialcrawl.dev/v1/instagram/audio/reels?audio_id=1392969992841787" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/search/hashtag — 5 credits (advanced)

Search Instagram posts by hashtag

- `hashtag` (required) — The hashtag to search for. The leading # is optional.
- `type` (optional, enum: top | recent | clips) — Ranking of the returned posts: `top` (default), `recent`, or `clips` (reels only).
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.
- `safe_url` (optional, boolean) — When true, returns URL-safe media links suitable for embedding.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/search/hashtag?hashtag=makeup" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/search/profiles — 1 credit (standard)

Search Instagram profiles by keyword

- `query` (required) — Bio or caption keyword/phrase to search for.
- `cursor` (optional, string) — The cursor returned by the previous response. In this version it is the next Google results page number.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/search/profiles?query=yoga" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/reels/trending — 5 credits (advanced)

Get trending Instagram reels

```bash
curl "https://www.socialcrawl.dev/v1/instagram/reels/trending" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/followers — 5 credits (advanced)

List Instagram followers

- `handle` (optional, string) — Instagram username without the @ symbol.
- `user_id` (optional, string) — Instagram numeric user ID. Use this for faster responses.
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/followers" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/following — 5 credits (advanced)

List Instagram following

- `handle` (optional, string) — Instagram username without the @ symbol.
- `user_id` (optional, string) — Instagram numeric user ID. Use this for faster responses.
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/following" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/similar — 5 credits (advanced)

List similar Instagram accounts

- `handle` (optional, string) — Instagram username without the @ symbol.
- `user_id` (optional, string) — Instagram numeric user ID. Use this for faster responses.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/similar" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/post/likers — 5 credits (advanced)

List Instagram post likers

- `url` (required) — URL of the Instagram post (a /p/ or /reel/ link).
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.
- `safe_url` (optional, boolean) — When true, returns URL-safe profile picture links suitable for embedding.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/post/likers?url=https://www.instagram.com/p/CnpPou9hWqq/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/post/stats — 5 credits (advanced)

Get Instagram post stats including the share count

- `url` (required) — URL of the Instagram post (a /p/, /reel/, or /tv/ link).
- `safe_url` (optional, boolean) — When true, returns URL-safe media links suitable for embedding.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/post/stats?url=https://www.instagram.com/p/CnpPou9hWqq/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/tagged — 5 credits (advanced)

List posts an Instagram user is tagged in

- `handle` (optional, string) — Instagram username without the @ symbol.
- `user_id` (optional, string) — Instagram numeric user ID. Use this for faster responses.
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.
- `safe_url` (optional, boolean) — When true, returns URL-safe media links suitable for embedding.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/tagged" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/location/posts — 5 credits (advanced)

List recent posts at an Instagram location

- `location_id` (required) — Instagram numeric location ID.
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.
- `safe_url` (optional, boolean) — When true, returns URL-safe media links suitable for embedding.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/location/posts?location_id=331004901" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/engagement — 5 credits (advanced)

Get Instagram engagement statistics

- `handle` (required) — Instagram username without the @ symbol.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/engagement?handle=mrbeast" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/search/location — 5 credits (advanced)

Search Instagram locations

- `query` (required) — Search keyword or phrase to find Instagram locations.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/search/location?query=Paris" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/username-suggestions — 5 credits (advanced)

Get Instagram username suggestions

- `query` (required) — Keyword to seed the username suggestions.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/username-suggestions?query=mrbeast" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/search/music — 5 credits (advanced)

Search Instagram music

- `query` (required) — Search keyword or phrase to find Instagram audio tracks.
- `cursor` (optional, string) — Pagination cursor. Use the `next_cursor` from the previous response to fetch the next page.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/search/music?query=beyonce" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/stories — 5 credits (advanced)

List an Instagram user's active stories

- `handle` (optional, string) — Instagram username without the @ symbol.
- `user_id` (optional, string) — Instagram numeric user ID. Use this for faster responses.
- `safe_url` (optional, boolean) — When true, returns URL-safe media links suitable for embedding.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/stories" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/story/download — 5 credits (advanced)

Download a single Instagram story

- `user_id` (optional, string) — Instagram numeric user ID of the story's author.
- `story_id` (optional, string) — ID of the individual story to download.
- `safe_url` (optional, boolean) — When true, returns URL-safe media links suitable for embedding.

**At least one of `story_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/story/download" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/music/trending — 5 credits (advanced)

List trending Instagram music

```bash
curl "https://www.socialcrawl.dev/v1/instagram/music/trending" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/profile/full — 5 credits (custom)

Instagram profile, recent posts, and computed analytics in one call.

- `handle` (optional, string)
- `posts` (optional, integer) — How many recent posts to fetch + average the computed metrics over (1–100, default 25).
- `cursor` (optional, string) — Pass a prior response's posts_cursor to deepen the post window.
- `include` (optional, string) — CSV subset of posts,computed (default both). include=computed drops the raw posts[] to save payload.

```bash
curl "https://www.socialcrawl.dev/v1/instagram/profile/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/profile/reels/full — 5 credits (advanced)

Instagram reels with views, likes, comments, and per-reel share counts where available, in one call.

- `handle` (optional, string) — Instagram username (with or without a leading @). Required unless user_id is given. The share-count leg needs a handle; a user_id-only call returns views/likes/comments with shares null (partial refund).
- `user_id` (optional, string) — Numeric Instagram user id. Alternative to handle.
- `cursor` (optional, string) — Opaque cursor from a prior response's next_cursor to page deeper.
- `limit` (optional, integer) — Return up to this many items in one call (1–50). The endpoint pages the underlying source server-side until it has collected this many (or runs out), and bills per upstream page consumed (5 credits/page). Omit for a single page.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/profile/reels/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/instagram/profile/posts/full — 5 credits (advanced)

Instagram posts with views, likes, comments, and per-post share counts where available, in one call.

- `handle` (optional, string) — Instagram username (with or without a leading @). Required unless user_id is given. The share-count leg needs a handle; a user_id-only call returns views/likes/comments with shares null (partial refund).
- `user_id` (optional, string) — Numeric Instagram user id. Alternative to handle.
- `cursor` (optional, string) — Opaque cursor from a prior response's next_cursor to page deeper.
- `limit` (optional, integer) — Return up to this many items in one call (1–50). The endpoint pages the underlying source server-side until it has collected this many (or runs out), and bills per upstream page consumed (5 credits/page). Omit for a single page.

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/instagram/profile/posts/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
