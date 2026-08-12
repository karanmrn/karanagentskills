# Apple App Store

9 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit), 4 advanced (5), 1 premium (10) — the exact cost is in each endpoint heading below.

**Latency:** Most Apple App Store endpoints are task-polled upstream — expect ~10–45s responses. Use a 60s timeout.

## GET /v1/app_store/app-search — 5 credits (advanced)

Search Apple App Store apps by keyword

- `query` (required) — Search keyword (e.g. 'photo editor').
- `country` (optional, string) — Storefront country as a DFS location name ('United States') or numeric location code ('2840'). Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.
- `depth` (optional, integer) — Number of results to retrieve (default 100, rounded up to multiples of 100, max 300).

```bash
curl "https://www.socialcrawl.dev/v1/app_store/app-search?query=photo editor" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/search-suggestions — 1 credit (standard)

Get Apple App Store search suggestions

- `query` (required) — Partial search keyword to autocomplete (e.g. 'reverse').
- `country` (optional, string) — ISO 3166-1 alpha-2 storefront country code. Defaults to 'us'.

```bash
curl "https://www.socialcrawl.dev/v1/app_store/search-suggestions?query=reverse" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/app-info — 5 credits (advanced)

Get full Apple App Store app details

- `app_id` (required) — Apple App Store numeric app id (e.g. '324684580'), from app-search.
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.

```bash
curl "https://www.socialcrawl.dev/v1/app_store/app-info?app_id=324684580" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/app-reviews — 5 credits (advanced)

Get Apple App Store reviews for an app

- `app_id` (required) — Apple App Store numeric app id (e.g. '324684580'), from app-search.
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.
- `depth` (optional, integer) — Number of reviews to retrieve (default 50, batches of 50, max 600).
- `sort_by` (optional, enum: most_recent | most_helpful) — Review ordering: `most_recent` (default) or `most_helpful`.
- `rating` (optional, integer) — Filter to a single star rating (1–5).

```bash
curl "https://www.socialcrawl.dev/v1/app_store/app-reviews?app_id=324684580" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/app-list — 5 credits (advanced)

Get an Apple App Store chart

- `app_collection` (required) — Chart to retrieve: top_free_ios, top_paid_ios, top_grossing_ios, top_free_ipad, top_paid_ipad, top_grossing_ipad, new_ios, new_free_ios, new_paid_ios.
- `app_category` (optional, enum: books | business | catalogs | education | entertainment | finance | food_and_drink | games | games_action | games_adventure | games_arcade | games_board | games_card | games_casino | games_dice | games_educational | games_family | games_music | games_puzzle | games_racing | games_role_playing | games_simulation | games_sports | games_strategy | games_trivia | games_word | health_and_fitness | lifestyle | magazines_and_newspapers | magazines_arts | magazines_automotive | magazines_weddings | magazines_business | magazines_children | magazines_computer | magazines_food | magazines_crafts | magazines_electronics | magazines_entertainment | magazines_fashion | magazines_health | magazines_history | magazines_home | magazines_literary | magazines_men | magazines_movies_and_music | magazines_politics | magazines_outdoors | magazines_family | magazines_pets | magazines_professional | magazines_regional | magazines_science | magazines_sports | magazines_teens | magazines_travel | magazines_women | medical | music | navigation | news | photo_and_video | productivity | reference | shopping | social_networking | sports | travel | utilities | weather) — Optional Apple App Store category to scope the chart (e.g. 'photo_and_video', 'games_puzzle').
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.
- `depth` (optional, integer) — Number of apps to retrieve (default 100, max 500).

```bash
curl "https://www.socialcrawl.dev/v1/app_store/app-list?app_collection=top_free_ios" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/app-listings-search — 10 credits (premium)

Search the Apple App Store listings database (paginated)

- `title` (required) — App title to search for (e.g. 'photo editor').
- `description` (optional, string) — Optional app-description text to match.
- `limit` (optional, integer) — Apps per page (1–50, default 20).
- `offset` (optional, integer) — Pagination offset (up to 10,000; use offset_token beyond).
- `offset_token` (optional, string) — Opaque deep-pagination cursor from a prior response.
- `filters` (optional, string) — Advanced DataForSEO filter expression as a JSON array.
- `country` (optional, string) — Storefront country as a DFS location name or numeric code. Defaults to the US.
- `language` (optional, string) — Language code (e.g. 'en'). Defaults to 'en'.

```bash
curl "https://www.socialcrawl.dev/v1/app_store/app-listings-search?title=photo editor" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/categories — 1 credit (standard)

List Apple App Store app categories

```bash
curl "https://www.socialcrawl.dev/v1/app_store/categories" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/locations — 1 credit (standard)

List supported Apple App Store storefront locations

```bash
curl "https://www.socialcrawl.dev/v1/app_store/locations" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/app_store/languages — 1 credit (standard)

List supported Apple App Store languages

```bash
curl "https://www.socialcrawl.dev/v1/app_store/languages" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
