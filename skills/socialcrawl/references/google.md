# Google

10 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 4 standard (1 credit), 6 advanced (5) — the exact cost is in each endpoint heading below.

**Latency:** Google Business, hotels, and some SERP resources are task-polled upstream — expect ~10–45s responses on those. Use a 60s timeout.

**Two-step:** `hotels/info` needs a `hotel_identifier` returned by `hotels/search` first.

## GET /v1/google/search — 1 credit (standard)

Google web search

- `query` (required) — Search keyword or phrase
- `region` (optional, string) — 2 letter country code, ie US, UK, CA, etc This will show results from that country
- `date_posted` (optional, enum: last-hour | last-day | last-week | last-month | last-year) — Date posted
- `page` (optional, integer) — Page number to retrieve

```bash
curl "https://www.socialcrawl.dev/v1/google/search?query=best restaurants in London" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/ad — 5 credits (advanced)

Get Google ad details

- `url` (required) — Ads Transparency Center CREATIVE URL — must include both the advertiser and creative segments (`…/advertiser/{AR…}/creative/{CR…}`). Get one from `/v1/google/company/ads`.

```bash
curl "https://www.socialcrawl.dev/v1/google/ad?url=https://adstransparency.google.com/advertiser/AR01614014350098432001/creative/CR10449491775734153217" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/adlibrary/advertisers/search — 5 credits (advanced)

Search Google Ad Library advertisers

- `query` (required) — Search keyword or phrase to find advertisers in the Google Ads Transparency Center.
- `region` (optional, string) — 2-letter country code to search in. Defaults to US.

```bash
curl "https://www.socialcrawl.dev/v1/google/adlibrary/advertisers/search?query=lululemon" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/company/ads — 5 credits (advanced)

List Google ads by company

- `domain` (optional, string) — Company domain name to look up ads for
- `advertiser_id` (optional, string) — The advertiser id of the company
- `topic` (optional, enum: all | political) — The topic to search for. If you search for 'political', you will also need to pass a 'region', like 'US' or 'AU'
- `region` (optional, string) — The region to search for. Defaults to anywhere
- `start_date` (optional, string) — Start date to search for. Format: YYYY-MM-DD
- `end_date` (optional, string) — End date to search for. Format: YYYY-MM-DD
- `platform` (optional, enum: google_maps | google_play | google_search | google_shopping | youtube) — Google surface to filter ads by (e.g. youtube, google_search)
- `format` (optional, enum: text | image | video) — Ad format to filter by: text, image, or video
- `get_ad_details` (optional, string) — Set to true to get the ad details. Will cost 25 credits.
- `cursor` (optional, string) — Cursor to paginate through results

**At least one of `domain` / `advertiser_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/google/company/ads" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/business/info — 1 credit (standard)

Get a Google Business Profile

- `keyword` (optional, string) — Business name + address (e.g. 'Irving Farm New York 645 5th Ave'). Use cid/place_id when known for an exact match.
- `cid` (optional, string) — Google customer id (cid) of the place — the most reliable identifier.
- `place_id` (optional, string) — Google place_id of the place.
- `location_name` (optional, string) — Geographic context as 'City,Region,Country' (default 'New York,New York,United States').
- `language_name` (optional, string) — Result language (default 'English').

**At least one of `keyword` / `cid` / `place_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/google/business/info" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/business/extended-reviews — 5 credits (advanced)

Get Google extended (multi-source) reviews

- `keyword` (optional, string) — Business name + address. Use cid/place_id for an exact match.
- `cid` (optional, string) — Google customer id (cid) of the place.
- `place_id` (optional, string) — Google place_id of the place.
- `location_name` (optional, string) — Geographic context as 'City,Region,Country'.
- `language_name` (optional, string) — Result language (default 'English').
- `depth` (optional, integer) — Number of reviews to return (default 20, step 20, max 1000).

**At least one of `keyword` / `cid` / `place_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/google/business/extended-reviews" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/business/updates — 1 credit (standard)

Get Google Business Profile posts (updates)

- `keyword` (optional, string) — Business name + location (e.g. 'Toyota of Manhattan New York').
- `cid` (optional, string) — Google customer id (cid) of the business.
- `location_name` (optional, string) — Geographic context as 'City,Region,Country'.
- `language_name` (optional, string) — Result language (default 'English').

**At least one of `keyword` / `cid` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/google/business/updates" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/business/questions — 5 credits (advanced)

Get Google Business Profile questions & answers

- `keyword` (optional, string) — Business name + location (e.g. 'Starbucks Reserve Roastery New York').
- `cid` (optional, string) — Google customer id (cid) of the business.
- `place_id` (optional, string) — Google place_id of the business.
- `location_name` (optional, string) — Geographic context as 'City,Region,Country'.
- `language_name` (optional, string) — Result language (default 'English').
- `depth` (optional, integer) — Number of questions to return (default 20).

**At least one of `keyword` / `cid` / `place_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/google/business/questions" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/hotels/search — 1 credit (standard)

Search Google hotels

- `keyword` (required) — Hotel search query (e.g. 'hotels in New York').
- `location_name` (optional, string) — Geographic context as 'City,Region,Country'.
- `language_name` (optional, string) — Result language (default 'English').
- `check_in` (optional, string) — Check-in date (YYYY-MM-DD). Defaults to the next day.
- `check_out` (optional, string) — Check-out date (YYYY-MM-DD). Defaults to one night.

```bash
curl "https://www.socialcrawl.dev/v1/google/hotels/search?keyword=hotels in New York" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/google/hotels/info — 5 credits (advanced)

Get Google hotel detail

- `hotel_identifier` (required) — Opaque hotel id returned by GET /v1/google/hotels/search.
- `location_name` (optional, string) — Geographic context as 'City,Region,Country'.
- `language_name` (optional, string) — Result language (default 'English').

```bash
curl "https://www.socialcrawl.dev/v1/google/hotels/info?hotel_identifier=ChkIoYjXwK-S_okHGg0vZy8xMW1fd3MzY243EAE" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
