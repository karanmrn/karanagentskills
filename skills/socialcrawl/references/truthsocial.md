# Truth Social

3 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 3 standard (1 credit) — the exact cost is in each endpoint heading below.

## GET /v1/truthsocial/profile — 1 credit (standard)

Get Truth Social user profile

- `handle` (required) — Truth Social username without the @ symbol

```bash
curl "https://www.socialcrawl.dev/v1/truthsocial/profile?handle=realDonaldTrump" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/truthsocial/user/posts — 1 credit (standard)

List Truth Social user posts

- `handle` (optional, string) — Truth Social username without the @ symbol
- `user_id` (optional, string) — Truth Social user id. Use this for faster response times. Trumps is 107780257626128497. It is the 'id' field in the profile endpoint.
- `next_max_id` (optional, string) — Used to paginate to next page
- `trim` (optional, boolean) — Set to true for a trimmed down version of the response

**At least one of `handle` / `user_id` is required.**

```bash
curl "https://www.socialcrawl.dev/v1/truthsocial/user/posts" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/truthsocial/post — 1 credit (standard)

Get Truth Social post details

- `url` (required) — Full URL of the Truth Social post

```bash
curl "https://www.socialcrawl.dev/v1/truthsocial/post?url=https://truthsocial.com/@realDonaldTrump/posts/123456789" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
