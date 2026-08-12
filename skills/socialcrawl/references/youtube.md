# YouTube

28 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 19 standard (1 credit), 5 advanced (5), 1 premium (10), 3 custom (flat/metered) — the exact cost is in each endpoint heading below.

## GET /v1/youtube/channel — 1 credit (standard)

Get YouTube channel info

- `channelId` (optional, string) — YouTube channel ID. Can pass a channelId, handle or url
- `handle` (optional, string) — YouTube channel handle without the @ symbol
- `url` (optional, string) — YouTube channel URL. Can pass a channelId, handle or url
- `hl` (optional, string) — Preferred response language for localized text (ISO 639-1, e.g. 'en', 'es', 'fr').
- `forUsername` (optional, string) — Legacy YouTube username (pre-handle) to look up.

**At least one of `channelId` / `handle` / `url` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/youtube/channel" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/channel/videos — 1 credit (standard)

List YouTube channel videos

- `channelId` (optional, string) — YouTube channel ID
- `handle` (optional, string) — YouTube channel handle without the @ symbol
- `sort` (optional, enum: latest | popular) — Sort by latest or popular
- `continuationToken` (optional, string) — Continuation token to get more videos. Get 'continuationToken' from previous response.
- `includeExtras` (optional, string) — This will get you the like + comment count and the description. To get the full details of the video, use the /v1/youtube/video endpoint. This will slow down the response slightly.
- `is_paid_promotions` (optional, string) — Set to 'true' to search YouTube's public paid product placement / sponsorship / endorsement surface — returns normal videos where the creator disclosed a paid promotion.

**At least one of `channelId` / `handle` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/youtube/channel/videos" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video — 1 credit (standard)

Get YouTube video details

- `url` (required) — Full URL of the YouTube video
- `language` (optional, string) — Preferred response language (mapped to Accept-Language header; not guaranteed due to YouTube localization behavior). 2 letter language code, ie 'en', 'es', 'fr' etc.
- `hl` (optional, string) — Preferred response language for localized text (ISO 639-1, e.g. 'en', 'es', 'fr').

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/videos — 5 credits (advanced)

Batch get YouTube video details (up to 1000)

- `ids` (required) — JSON array of BARE YouTube video ids (11 characters each, e.g. 'dQw4w9WgXcQ'), 1 to 1000 per request. Unlike GET /v1/youtube/video, full watch URLs are not accepted here.
- `hl` (optional, string) — Preferred response language for localized text (ISO 639-1, e.g. 'en', 'ko').
- `include_localizations` (optional, boolean) — When true, includes per-language title/description localizations in each item's ext.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/videos?ids=dQw4w9WgXcQ,9bZkp7q19f0" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/channels — 5 credits (advanced)

Batch get YouTube channel details (up to 1000)

- `ids` (required) — JSON array of BARE YouTube channel ids (24 characters, starting with 'UC', e.g. 'UC_x5XG1OV2P6uZZ5FSM9Ttw'), 1 to 1000 per request. Unlike GET /v1/youtube/channel, channel URLs/handles are not accepted here.
- `hl` (optional, string) — Preferred response language for localized text (ISO 639-1, e.g. 'en', 'ko').
- `include_localizations` (optional, boolean) — When true, includes per-language localizations in each item's ext.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/channels?ids=UC_x5XG1OV2P6uZZ5FSM9Ttw,UCX6OQ3DkcsbYNE6H8uQQuVA" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/transcripts — 3 credits (custom)

Up to 100 YouTube video ids → one transcript per row, failed ids refunded.

- `ids` (required) — JSON array of 1–100 BARE YouTube video ids (11 characters each, e.g. 'dQw4w9WgXcQ'). Full watch URLs are not accepted here.
- `language` (optional, string) — Preferred caption-track language (2-letter code, e.g. 'en', 'ko'). Falls back to the default track when absent or unavailable.
- `format` (optional, string) — `text` (default) returns the whole transcript as one joined string; `segments` returns timestamped `[{start_ms, duration_ms, text}]`.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/transcripts?ids=dQw4w9WgXcQ,9bZkp7q19f0" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/sponsors — 10 credits (premium)

Detect sponsors of a YouTube video

- `url` (required) — Full URL of the YouTube video or short
- `language` (optional, string) — 2 letter language code used for transcript lookup, ie 'en', 'es', 'fr' etc.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/sponsors?url=https://www.youtube.com/watch?v=AVO0ifle-OU" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/comments — 1 credit (standard)

List YouTube video comments

- `url` (required) — Full URL of the YouTube video to fetch comments for
- `continuationToken` (optional, string) — Continuation token to get more comments. Get 'continuationToken' from previous response.
- `order` (optional, enum: top | newest) — Order of comments
- `searchTerm` (optional, string) — Filter comments to those containing this search term.
- `format` (optional, enum: html | plainText) — Text format for comment bodies — 'html' (default) or 'plainText'.
- `max_results` (optional, integer) — Maximum number of comments to return per page.
- `channel_id` (optional, string) — YouTube channel id to fetch channel-level community comments for (instead of a video's comments).

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/comments?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/comment/replies — 1 credit (standard)

List YouTube comment replies

- `continuationToken` (required) — Continuation token for the comment replies. Use 'repliesContinuationToken' from the Comments endpoint, or 'continuationToken' from a previous replies response to paginate.
- `format` (optional, enum: html | plainText) — Text format for reply bodies — 'html' (default) or 'plainText'.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/comment/replies?continuationToken=Eg0SC2RRdzR3OVdnWGNRGAYygwEaUBIa..." \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/search — 1 credit (standard)

Search YouTube

- `query` (required) — Search keyword or phrase.
- `uploadDate` (optional, enum: today | this_week | this_month | this_year) — Upload date filter.
- `sortBy` (optional, enum: relevance | popular) — Sort order — relevance or popular.
- `type` (optional, enum: videos | shorts | channels | playlists) — Type of content to return.
- `duration` (optional, enum: under_3_min | between_3_and_20_min | over_20_min) — Video duration filter. Only applies to videos (not shorts).
- `region` (optional, string) — 2-letter country code of the country to put the proxy in.
- `continuationToken` (optional, string) — Continuation token to get more results. Get `continuationToken` from a previous response.
- `includeExtras` (optional, string) — Set to `true` to include like + comment count and description. For full per-video details use `/v1/youtube/video`. Slows the response slightly.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/search?query=javascript tutorial" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/channel/shorts — 1 credit (standard)

List YouTube channel shorts

- `handle` (optional, string) — YouTube channel handle without the @ symbol
- `channelId` (optional, string) — Can pass channelId or handle
- `sort` (optional, enum: newest | popular) — Sort by newest or popular
- `continuationToken` (optional, string) — Continuation token to get more videos. Get 'continuationToken' from previous response.

**At least one of `channelId` / `handle` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/youtube/channel/shorts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/community-post — 1 credit (standard)

Get YouTube community post

- `url` (required) — Full URL of the YouTube community post

```bash
curl "https://www.socialcrawl.dev/v1/youtube/community-post?url=https://www.youtube.com/post/Ugkxvj2KoApYAXoqLWnKVr6zZe5JjeHrQeP8" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/playlist — 1 credit (standard)

Get YouTube playlist

- `playlist_id` (required) — YouTube playlist ID
- `cursor` (optional, string) — Pagination cursor from a previous response — fetches the next page.
- `channel_id` (optional, string) — YouTube channel id — pages that channel's uploads instead of a playlist.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/playlist?playlist_id=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/search/hashtag — 1 credit (standard)

Search YouTube by hashtag

- `hashtag` (required) — Hashtag to search for without the # symbol
- `continuationToken` (optional, string) — Continuation token to get more videos. Get 'continuationToken' from previous response.
- `type` (optional, enum: all | shorts) — Search for all types of content or only shorts

```bash
curl "https://www.socialcrawl.dev/v1/youtube/search/hashtag?hashtag=shorts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/shorts/trending — 5 credits (advanced)

Get trending YouTube shorts

```bash
curl "https://www.socialcrawl.dev/v1/youtube/shorts/trending" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/transcript — 3 credits (custom)

Get YouTube video transcript

- `url` (required) — Full URL of the YouTube video
- `language` (optional, string) — 2 letter language code, ie 'en', 'es', 'fr' etc. If the transcript is not available in the language you specify, the transcript will be null.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/channel/playlists — 1 credit (standard)

List a YouTube channel's playlists

- `channelId` (optional, string) — YouTube channel ID.
- `handle` (optional, string) — YouTube channel handle (with or without @).
- `continuationToken` (optional, string) — Continuation token from a previous response — fetches the next page.

**At least one of `channelId` / `handle` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/youtube/channel/playlists" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/channel/lives — 1 credit (standard)

List a YouTube channel's live streams

- `channelId` (optional, string) — YouTube channel ID.
- `handle` (optional, string) — YouTube channel handle (with or without @).
- `continuationToken` (optional, string) — Continuation token from a previous response — fetches the next page.

**At least one of `channelId` / `handle` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/youtube/channel/lives" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/channel/community-posts — 1 credit (standard)

List a YouTube channel's community posts

- `channelId` (optional, string) — YouTube channel ID.
- `handle` (optional, string) — YouTube channel handle (with or without @).
- `continuationToken` (optional, string) — Continuation token from a previous response — fetches the next page.

**At least one of `channelId` / `handle` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/youtube/channel/community-posts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/videos/trending — 1 credit (standard)

Get trending YouTube videos

- `region` (optional, string) — ISO 3166-1 alpha-2 country code (e.g. US, GB, KR).
- `category` (optional, string) — YouTube video category id (e.g. 10 = Music, 24 = Entertainment).
- `language` (optional, string) — Localization language (ISO 639-1) for titles/metadata.
- `max_results` (optional, integer) — Maximum number of videos to return (1–50).
- `cursor` (optional, string) — Pagination cursor from a previous response — fetches the next page.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/videos/trending" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/playlist/items — 1 credit (standard)

List the videos in a YouTube playlist

- `playlist_id` (required) — YouTube playlist id (the value after `list=` in a playlist URL).
- `cursor` (optional, string) — Pagination cursor from a previous response — fetches the next page.
- `channel_id` (optional, string) — YouTube channel id — pages that channel's uploads instead of a playlist.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/playlist/items?playlist_id=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/search/advanced — 1 credit (standard)

Advanced YouTube video search

- `query` (required) — Search query.
- `order` (optional, string) — Sort order: date, rating, relevance (default), title, videoCount, viewCount.
- `duration` (optional, string) — Video length: short (<4m), medium (4–20m), long (>20m), any.
- `event_type` (optional, string) — Broadcast type: live, upcoming, completed.
- `license` (optional, string) — License filter: creativeCommon, youtube, any.
- `category` (optional, string) — YouTube video category id (e.g. 10 = Music).
- `region` (optional, string) — ISO 3166-1 alpha-2 country code.
- `language` (optional, string) — Preferred result language (ISO 639-1).
- `published_after` (optional, string) — RFC-3339 datetime lower bound (e.g. 2026-01-01T00:00:00Z).
- `published_before` (optional, string) — RFC-3339 datetime upper bound.
- `channel_id` (optional, string) — Restrict results to a single channel id.
- `max_results` (optional, integer) — Maximum number of videos to return (1–50).
- `cursor` (optional, string) — Pagination cursor from a previous response — fetches the next page.
- `safe_search` (optional, string) — Safe-search filter: none, moderate, strict.
- `video_caption` (optional, string) — Caption filter: any, closedCaption, none.
- `video_definition` (optional, string) — Quality filter: any, high, standard.
- `video_dimension` (optional, string) — Dimension filter: 2d, 3d, any.
- `video_embeddable` (optional, string) — Restrict to embeddable videos: true, any.
- `video_type` (optional, string) — Type filter: any, episode, movie.
- `topic_id` (optional, string) — Restrict to a Freebase topic id (e.g. /m/04rlf for music).
- `location` (optional, string) — Latitude,longitude center for a geo search (e.g. 37.42307,-122.08427). Must be used together with location_radius.
- `location_radius` (optional, string) — Radius around location with a unit suffix (e.g. 50km, 10mi). Must be used together with location.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/search/advanced?query=lofi hip hop" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/search/suggestions — 1 credit (standard)

Get YouTube search suggestions

- `query` (required) — Partial search query to autocomplete.
- `region` (optional, string) — ISO 3166-1 alpha-2 country code to localize suggestions.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/search/suggestions?query=lofi" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/audio — 5 credits (advanced)

Get a YouTube video's audio file streams

- `url` (required) — Full URL of the YouTube video.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/audio?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/files — 5 credits (advanced)

Get a YouTube video's video file streams

- `url` (required) — Full URL of the YouTube video.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/files?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/subtitles — 1 credit (standard)

Get a YouTube video's subtitle files

- `url` (required) — Full URL of the YouTube video.
- `format` (optional, string) — Subtitle file format filter (e.g. srt, vtt, ttml, json3, srv1).

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/subtitles?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/video/thumbnails — 1 credit (standard)

Get a YouTube video's thumbnail files

- `url` (required) — Full URL of the YouTube video.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/video/thumbnails?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/youtube/profile/full — 5 credits (custom)

YouTube profile, recent posts, and computed analytics in one call.

- `handle` (optional, string)
- `channelId` (optional, string)
- `url` (optional, string)
- `posts` (optional, integer) — How many recent posts to fetch + average the computed metrics over (1–100, default 25).
- `cursor` (optional, string) — Pass a prior response's posts_cursor to deepen the post window.
- `include` (optional, string) — CSV subset of posts,computed (default both). include=computed drops the raw posts[] to save payload.

```bash
curl "https://www.socialcrawl.dev/v1/youtube/profile/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
