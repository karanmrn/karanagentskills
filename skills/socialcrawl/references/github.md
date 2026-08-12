# GitHub

12 endpoints. All are GET requests against `https://www.socialcrawl.dev` with header `x-api-key: $SOCIALCRAWL_API_KEY`.

**Credit costs:** 9 standard (1 credit), 2 advanced (5), 1 premium (10) — the exact cost is in each endpoint heading below.

## GET /v1/github/profile — 1 credit (standard)

Get a GitHub user profile

- `handle` (required) — GitHub username — 1–39 chars, alphanumeric + non-consecutive hyphens, no leading/trailing hyphen.

```bash
curl "https://www.socialcrawl.dev/v1/github/profile?handle=octocat" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/repo — 1 credit (standard)

Get a GitHub repository

- `url` (required) — GitHub repo URL — `https://github.com/{owner}/{repo}`.

```bash
curl "https://www.socialcrawl.dev/v1/github/repo?url=https://github.com/octocat/Hello-World" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/profile/repos — 1 credit (standard)

List a GitHub user's repositories

- `handle` (required) — GitHub username.
- `type` (optional, enum: all | owner | member) — Filter — `all`, `owner`, or `member`. Defaults to `owner`.
- `sort` (optional, enum: created | updated | pushed | full_name) — Sort field — `created`, `updated`, `pushed`, or `full_name`. Defaults to `full_name`.
- `direction` (optional, enum: asc | desc) — `asc` or `desc`. Defaults to `asc` for full_name, `desc` otherwise.
- `per_page` (optional, integer) — Repos per page (1–100). Defaults to 30.
- `page` (optional, integer) — 1-indexed page number for pagination.

```bash
curl "https://www.socialcrawl.dev/v1/github/profile/repos?handle=octocat" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/repo/readme — 1 credit (standard)

Get a repository's README

- `url` (required) — GitHub repo URL — `https://github.com/{owner}/{repo}`.

```bash
curl "https://www.socialcrawl.dev/v1/github/repo/readme?url=https://github.com/octocat/Hello-World" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/repo/releases — 1 credit (standard)

List a repository's releases

- `url` (required) — GitHub repo URL — `https://github.com/{owner}/{repo}`.
- `per_page` (optional, integer) — Releases per page (1–100). Defaults to 30.
- `page` (optional, integer) — 1-indexed page number.

```bash
curl "https://www.socialcrawl.dev/v1/github/repo/releases?url=https://github.com/facebook/react" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/repo/issues — 1 credit (standard)

List a repository's issues (and PRs)

- `url` (required) — GitHub repo URL — `https://github.com/{owner}/{repo}`.
- `type` (optional, enum: issue | pr | all) — Filter the unified issues+PRs list — `issue` returns only issues, `pr` returns only pull requests, `all` (default) returns both. Each item also carries `post.ext.type` (`issue`/`pull_request`).
- `state` (optional, enum: open | closed | all) — `open`, `closed`, or `all`. Defaults to `open`.
- `labels` (optional, string) — Comma-separated label names (e.g. `bug,help wanted`).
- `sort` (optional, enum: created | updated | comments) — `created`, `updated`, or `comments`. Defaults to `created`.
- `direction` (optional, enum: asc | desc) — `asc` or `desc`. Defaults to `desc`.
- `since` (optional, string) — Only issues updated at or after this ISO 8601 timestamp.
- `per_page` (optional, integer) — Issues per page (1–100). Defaults to 30.
- `page` (optional, integer) — 1-indexed page number.

```bash
curl "https://www.socialcrawl.dev/v1/github/repo/issues?url=https://github.com/facebook/react" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/issue — 1 credit (standard)

Get a single issue or pull request

- `url` (required) — GitHub HTML URL — `https://github.com/{owner}/{repo}/issues/{n}` or `/pull/{n}`.

```bash
curl "https://www.socialcrawl.dev/v1/github/issue?url=https://github.com/facebook/react/issues/27522" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/issue/comments — 1 credit (standard)

Get comments on an issue or pull request

- `url` (required) — GitHub HTML URL of the issue or PR.
- `since` (optional, string) — Only comments updated at or after this ISO 8601 timestamp.
- `per_page` (optional, integer) — Comments per page (1–100). Defaults to 30.
- `page` (optional, integer) — 1-indexed page number.

```bash
curl "https://www.socialcrawl.dev/v1/github/issue/comments?url=https://github.com/facebook/react/issues/27522" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/search — 1 credit (standard)

Search GitHub issues and pull requests

- `query` (required) — GitHub search query (uses GitHub's qualifier syntax — see https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests).
- `sort` (optional, enum: reactions | comments | created | updated) — Sort field — `reactions`, `comments`, `created`, `updated`. Defaults to best-match relevance.
- `order` (optional, enum: asc | desc) — `asc` or `desc`. Defaults to `desc`.
- `per_page` (optional, integer) — Results per page (1–100). Defaults to 30.
- `page` (optional, integer) — 1-indexed page number.

```bash
curl "https://www.socialcrawl.dev/v1/github/search?query=repo:vercel/next.js is:issue is:open" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/repo/top-issues — 5 credits (advanced)

Top feature request and top complaint for a repository

- `url` (required) — GitHub repo URL — `https://github.com/{owner}/{repo}`.

```bash
curl "https://www.socialcrawl.dev/v1/github/repo/top-issues?url=https://github.com/facebook/react" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/repo/dossier — 5 credits (advanced)

Full project dossier for a repository

- `url` (required) — GitHub repo URL — `https://github.com/{owner}/{repo}`.

```bash
curl "https://www.socialcrawl.dev/v1/github/repo/dossier?url=https://github.com/facebook/react" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/github/user/profile-velocity — 10 credits (premium)

User contribution velocity dossier

- `handle` (required) — GitHub username.
- `depth` (optional, enum: quick | default | deep) — `quick`, `default`, or `deep`. Defaults to `default`. Trades off upstream calls vs. dossier richness.

```bash
curl "https://www.socialcrawl.dev/v1/github/user/profile-velocity?handle=octocat" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
