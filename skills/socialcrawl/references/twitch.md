# Twitch

4 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/twitch/profile — 1 credit (standard)

Get Twitch streamer profile

- `handle` (required) — Twitch username

```bash
curl "https://www.socialcrawl.dev/v1/twitch/profile?handle=ninja" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitch/clip — 1 credit (standard)

Get Twitch clip details

- `url` (required) — Full URL of the Twitch clip

```bash
curl "https://www.socialcrawl.dev/v1/twitch/clip?url=https://www.twitch.tv/ninja/clip/ExampleClipSlug" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitch/user/videos — 1 credit (standard)

List a Twitch user's videos

- `handle` (required) — Twitch username.
- `filter_by` (optional, enum: HIGHLIGHT | UPLOAD) — Filter the returned videos by type — `HIGHLIGHT` or `UPLOAD`. (Archived past broadcasts are not currently available upstream.)
- `sort_by` (optional, enum: TIME | VIEWS) — Sort order — `TIME` (newest first) or `VIEWS`.

```bash
curl "https://www.socialcrawl.dev/v1/twitch/user/videos?handle=ishowspeed" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/twitch/user/schedule — 1 credit (standard)

Get a Twitch user's stream schedule

- `handle` (required) — Twitch username.

```bash
curl "https://www.socialcrawl.dev/v1/twitch/user/schedule?handle=kaicenat" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
