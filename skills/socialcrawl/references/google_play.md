# Google Play

9 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit), 4 advanced (5), 1 premium (10) — the exact cost is in each endpoint heading below.

**Latency:** Most Google Play endpoints are task-polled upstream — expect ~10–45s responses. Use a 60s timeout.

## GET /v1/google_play/app-search — 5 credits (advanced)

Search Google Play apps by keyword

- `query` (required) — Search keyword (e.g. 'photo editor').
- `country` (optional, string) — Storefront country as a DFS location name ('United States') or numeric location code ('2840'). Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.
- `depth` (optional, integer) — Number of results to retrieve (default 30, rounded up to multiples of 30, max 300).

```bash
curl "https://www.socialcrawl.dev/v1/google_play/app-search?query=photo editor" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/search-suggestions — 1 credit (standard)

Get Google Play search suggestions

- `query` (required) — Partial search keyword to autocomplete (e.g. 'reverse').
- `country` (optional, string) — ISO 3166-1 alpha-2 storefront country code. Defaults to 'us'.
- `language` (optional, string) — ISO 639-1 language code. Defaults to 'en'.

```bash
curl "https://www.socialcrawl.dev/v1/google_play/search-suggestions?query=reverse" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/app-info — 5 credits (advanced)

Get full Google Play app details

- `app_id` (required) — Google Play package name (e.g. 'com.spotify.music'), from app-search.
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.

```bash
curl "https://www.socialcrawl.dev/v1/google_play/app-info?app_id=com.spotify.music" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/app-reviews — 5 credits (advanced)

Get Google Play reviews for an app

- `app_id` (required) — Google Play package name (e.g. 'com.spotify.music'), from app-search.
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.
- `depth` (optional, integer) — Number of reviews to retrieve (default 150, batches of 150, max 600).
- `sort_by` (optional, enum: newest | most_relevant) — Review ordering: `newest` (default) or `most_relevant`.
- `rating` (optional, integer) — Filter to a single star rating (1–5).

```bash
curl "https://www.socialcrawl.dev/v1/google_play/app-reviews?app_id=com.spotify.music" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/app-list — 5 credits (advanced)

Get a Google Play store chart

- `app_collection` (required) — Chart to retrieve: topselling_free, topselling_paid, topgrossing, movers_shakers, topselling_new_free, topselling_new_paid.
- `app_category` (optional, enum: art_and_design | auto_and_vehicles | beauty | books_and_reference | business | comics | communication | dating | education | entertainment | events | finance | food_and_drink | health_and_fitness | house_and_home | libraries_and_demo | lifestyle | maps_and_navigation | medical | music_and_audio | news_and_magazines | parenting | personalization | photography | productivity | shopping | social | sports | tools | travel_and_local | video_players | android_wear | watch_face | weather | game | game_action | game_adventure | game_arcade | game_board | game_card | game_casino | game_casual | game_educational | game_music | game_puzzle | game_racing | game_role_playing | game_simulation | game_sports | game_strategy | game_trivia | game_word | family) — Optional Google Play category to scope the chart (e.g. 'photography', 'game_puzzle').
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.
- `depth` (optional, integer) — Number of apps to retrieve (default 100, max 500).

```bash
curl "https://www.socialcrawl.dev/v1/google_play/app-list?app_collection=topselling_free" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/app-listings-search — 10 credits (premium)

Search the Google Play listings database (paginated)

- `title` (required) — App title to search for (e.g. 'photo editor').
- `description` (optional, string) — Optional app-description text to match.
- `limit` (optional, integer) — Apps per page (1–50, default 20).
- `offset` (optional, integer) — Pagination offset (up to 10,000; use offset_token beyond).
- `offset_token` (optional, string) — Opaque deep-pagination cursor from a prior response.
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array.
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.

```bash
curl "https://www.socialcrawl.dev/v1/google_play/app-listings-search?title=photo editor" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/categories — 1 credit (standard)

List Google Play app categories

```bash
curl "https://www.socialcrawl.dev/v1/google_play/categories" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/locations — 1 credit (standard)

List supported Google Play storefront locations

```bash
curl "https://www.socialcrawl.dev/v1/google_play/locations" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google_play/languages — 1 credit (standard)

List supported Google Play languages

```bash
curl "https://www.socialcrawl.dev/v1/google_play/languages" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
