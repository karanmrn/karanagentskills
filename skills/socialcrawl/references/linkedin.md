# LinkedIn

44 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 3 standard (1 credit), 34 advanced (5), 6 premium (10), 1 custom (flat/metered) — the exact cost is in each endpoint heading below.

## GET /v1/linkedin/profile — 5 credits (advanced)

Get LinkedIn user profile

- `url` (required) — Full URL of the LinkedIn profile page

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/company — 5 credits (advanced)

Get LinkedIn company page

- `url` (required) — Full URL of the LinkedIn company page

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/company?url=https://www.linkedin.com/company/microsoft/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/post — 5 credits (advanced)

Get LinkedIn post details

- `url` (required) — Full URL of the LinkedIn post

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/post?url=https://www.linkedin.com/posts/williamhgates_example-activity-1234567890" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/search/people — 10 credits (premium)

Search LinkedIn people

- `query` (required) — Name or display-name keyword to search for (e.g. 'Bill Gates').
- `page` (optional, string) — Page number for pagination (default 1).
- `first_name` (optional, string) — Filter by first name.
- `last_name` (optional, string) — Filter by last name.
- `title` (optional, string) — Filter by job title or headline.
- `current_company` (optional, string) — Filter by current company ID (comma-separated for multiple).
- `past_company` (optional, string) — Filter by a previously-worked company ID.
- `school` (optional, string) — Filter by school ID.
- `industry` (optional, string) — Filter by industry ID.
- `geocode_location` (optional, string) — Filter by location geocode ID.
- `profile_language` (optional, string) — Filter by profile language (ISO 2-letter code, e.g. 'en').
- `service_category` (optional, string) — Filter by service-category ID.
- `follower_of` (optional, string) — Return people who follow a specific member URN.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/search/people?query=Bill Gates" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/company/people — 10 credits (premium)

List people at a LinkedIn company

- `company_id` (required) — LinkedIn numeric company ID (from /v1/linkedin/company).
- `page` (optional, string) — Page number for pagination (default 1).

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/company/people?company_id=1035" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/post/comments — 5 credits (advanced)

Get LinkedIn post comments

- `url` (required) — Full URL of the LinkedIn post (or its activity id).
- `page` (optional, string) — Page number for pagination (default 1).
- `post_type` (optional, string) — Upstream post type: 'activity' (default) or 'ugc'.
- `sort_order` (optional, string) — Comment ordering: 'relevance' or 'recent'.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/post/comments?url=https://www.linkedin.com/feed/update/urn:li:activity:7244804629786419202" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/posts — 5 credits (advanced)

List a LinkedIn member's posts

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `cursor` (optional, string)
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/posts?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/reactions — 5 credits (advanced)

List posts a LinkedIn member reacted to

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `cursor` (optional, string)
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/reactions?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/post/reposts — 5 credits (advanced)

List reposts of a LinkedIn post

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `cursor` (optional, string)
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/post/reposts?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/group/posts — 5 credits (advanced)

List posts in a LinkedIn group

- `group_id` (required) — LinkedIn numeric group ID.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/group/posts?group_id=62438" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/company/affiliated-pages — 5 credits (advanced)

List a company's affiliated/showcase pages

- `company_id` (required) — LinkedIn numeric company ID (from /v1/linkedin/company).

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/company/affiliated-pages?company_id=1035" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/post/comments/replies — 5 credits (advanced)

List replies to a LinkedIn comment

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `comment_id` (required) — LinkedIn comment ID (from /post/comments).
- `cursor` (optional, string)
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/post/comments/replies?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/experiences — 5 credits (advanced)

List a member's work experiences

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/experiences?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/educations — 5 credits (advanced)

List a member's education history

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/educations?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/skills — 5 credits (advanced)

List a member's skills

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/skills?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/honors — 5 credits (advanced)

List a member's honors and awards

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/honors?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/certifications — 5 credits (advanced)

List a member's licenses and certifications

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/certifications?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/publications — 5 credits (advanced)

List a member's publications

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/publications?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/volunteers — 5 credits (advanced)

List a member's volunteer experiences

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/volunteers?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/recommendations — 5 credits (advanced)

List recommendations for a member

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)
- `type` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/recommendations?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/interests/companies — 5 credits (advanced)

List companies a member follows

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/interests/companies?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/interests/groups — 5 credits (advanced)

List groups a member follows

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/interests/groups?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/images — 5 credits (advanced)

List a member's image posts

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `cursor` (optional, string)
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/images?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/videos — 5 credits (advanced)

List a member's video posts

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `cursor` (optional, string)
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/videos?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/comments — 5 credits (advanced)

List a member's comments

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `cursor` (optional, string)
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/comments?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/post/reactions — 10 credits (premium)

List reactors on a LinkedIn post

- `url` (required) — Full URL of the LinkedIn profile, company, or post.
- `page` (optional, string)
- `type` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/post/reactions?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/company/jobs — 10 credits (premium)

List a company's job postings

- `company_id` (required) — LinkedIn numeric company ID (from /v1/linkedin/company).
- `page` (optional, string)
- `date_posted` (optional, string)
- `experience_level` (optional, string)
- `job_type` (optional, string)
- `remote` (optional, string)
- `easy_apply` (optional, string)
- `sort_by` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/company/jobs?company_id=1035" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/search/jobs — 10 credits (premium)

Search LinkedIn jobs

- `query` (required) — Search keyword.
- `page` (optional, string)
- `date_posted` (optional, string)
- `experience_level` (optional, string)
- `job_type` (optional, string)
- `remote` (optional, string)
- `easy_apply` (optional, string)
- `sort_by` (optional, string)
- `company` (optional, string)
- `geocode` (optional, string)
- `industry_ids` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/search/jobs?query=marketing" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/search/location — 1 credit (standard)

Resolve a location to a LinkedIn geocode id

- `query` (required) — Search keyword.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/search/location?query=marketing" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/search/schools — 1 credit (standard)

Search LinkedIn schools

- `query` (required) — Search keyword.
- `page` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/search/schools?query=marketing" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/search/industry — 1 credit (standard)

Resolve an industry name to a LinkedIn industry id

- `query` (required) — Search keyword.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/search/industry?query=marketing" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/about — 5 credits (advanced)

Get a member's profile metadata (joined date, freshness)

- `url` (required) — Full URL of the LinkedIn profile, company, or post.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/about?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/contact — 5 credits (advanced)

Get a member's public contact info

- `url` (required) — Full URL of the LinkedIn profile, company, or post.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/contact?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/stats — 5 credits (advanced)

Get a member's follower + connection counts

- `url` (required) — Full URL of the LinkedIn profile, company, or post.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/stats?url=https://www.linkedin.com/in/williamhgates/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/company/job-count — 5 credits (advanced)

Get a company's open job count

- `company_id` (required) — LinkedIn numeric company ID (from /v1/linkedin/company).

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/company/job-count?company_id=1035" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/company/insights — 5 credits (advanced)

Get aggregate insights about a company's members

- `company_id` (required) — LinkedIn numeric company ID (from /v1/linkedin/company).

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/company/insights?company_id=1035" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/group — 5 credits (advanced)

Get LinkedIn group details

- `group_id` (required) — LinkedIn numeric group ID.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/group?group_id=62438" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/job — 5 credits (advanced)

Get LinkedIn job details

- `id` (required) — LinkedIn job ID.
- `include_skills` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/job?id=4019392600" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/company/posts — 5 credits (advanced)

List LinkedIn company posts

- `company_id` (required) — LinkedIn numeric company ID (from /v1/linkedin/company).
- `page` (optional, string) — Page number for pagination (default 1).
- `sort_by` (optional, string) — Post ordering: 'top' or 'recent'.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/company/posts?company_id=1035" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/ad — 5 credits (advanced)

Get LinkedIn ad details

- `url` (required) — Full URL of the LinkedIn ad

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/ad?url=https://www.linkedin.com/ad-library/detail/666281156" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/ads/search — 5 credits (advanced)

Search LinkedIn ads

- `company` (optional, string) — The company name to search for. 'Microsoft' for example
- `keyword` (optional, string) — The keyword to search for
- `companyId` (optional, string) — The company id to search for
- `countries` (optional, string) — Comma separated list of countries. Example: US,CA,MX
- `startDate` (optional, string) — Start date to search for. Format: YYYY-MM-DD
- `endDate` (optional, string) — End date to search for. Format: YYYY-MM-DD
- `paginationToken` (optional, string) — Pagination token to paginate through results

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/ads/search" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/search/posts — 5 credits (advanced)

Search public LinkedIn posts by keyword

- `query` (required) — Keyword or phrase to search for in public LinkedIn posts.
- `page` (optional, string)
- `sort_by` (optional, string)
- `date_posted` (optional, string) — Date filter based on Google-indexed results.
- `content_type` (optional, string)
- `from_company` (optional, string)
- `from_member` (optional, string)

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/search/posts?query=ai agents" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/post/transcript — 10 credits (premium)

Get a LinkedIn post video transcript

- `url` (required) — Full URL of the LinkedIn post to transcribe.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/post/transcript?url=https://www.linkedin.com/posts/gemini-35-flash-is-a-step-forward-for-google-ugcPost-7465082215316525056-MHBd/" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/linkedin/profile/full — 5 credits (custom)

LinkedIn company profile, recent posts, and computed analytics in one call.

- `url` (optional, string)
- `posts` (optional, integer) — How many recent posts to fetch + average the computed metrics over (1–100, default 25).
- `cursor` (optional, string) — Pass a prior response's posts_cursor to deepen the post window.
- `include` (optional, string) — CSV subset of posts,computed (default both). include=computed drops the raw posts[] to save payload.

```bash
curl "https://www.socialcrawl.dev/v1/linkedin/profile/full" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
