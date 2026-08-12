# Monitors

The stateful, scheduled wrapper around any SocialCrawl recipe. A monitor re-runs a registered endpoint or a Prism composite on a cadence, delivers each result to a signed webhook, evaluates alert rules, and accumulates a per-run time-series you can read back. *"Prism answers once; monitors watch it for you."*

Monitors are **not** registry endpoints — they live at `/v1/monitors/*`, use methods beyond GET (POST/PATCH/DELETE), and are **not** counted in the 357-endpoint total. Auth is the same `x-api-key` header.

**Billing:** managing monitors (create / list / get / runs / timeseries / pause / delete) costs **0 credits**. Each *scheduled run* bills the underlying recipe's normal cost **plus 1 credit** (e.g. a daily `prism/reputation` monitor costs 30 + 1 = 31 credits per run). Skipped runs (insufficient balance) are never charged, and a run whose recipe returns `ok:false` is fully refunded. The `create` response returns `estimated_cost_per_run` and `estimated_monthly_cost`. The webhook auto-pauses after 10 consecutive delivery failures.

## POST /v1/monitors — create a monitor

Body (JSON):
- `recipe` (required, string) — the recipe to run each cadence: any registered endpoint or Prism composite as `platform/resource` (e.g. `prism/brand-mentions`, `tiktok/profile`).
- `cadence` (required) — `"hourly"`, `"daily"`, `"weekly"`, or `{ "cron": "0 9 * * 1" }`.
- `webhook_url` (required, string) — HTTPS endpoint that receives each run, signed with `x-socialcrawl-signature` (HMAC-SHA256, timestamped).
- `params` (optional, object) — parameters passed to the recipe on every run (e.g. `{ "keyword": "acme" }`).
- `name` (optional, string) — human-readable label.
- `alert_rules` (optional, array) — `[{ "metric", "op", "value", "window"? }]`. Ops: `gt`, `lt`, `gte`, `lte`, `abs_change_gt`, `pct_change_gt`, `pct_change_lt` (the change ops compare a run to the previous comparable run; `window` is `1d` | `1w`).
- `suppress_webhook_unless_alert` (optional, boolean) — only fire the webhook when an alert rule trips (default false).
- `output_schema` (optional, object) — JSON schema to shape the delivered payload.
- `webhook_secret` (optional, string, 8–200 chars) — your own signing secret; otherwise one is generated and returned **once** in the create response.

Returns `201` with `{ monitor, webhook_secret }` and backfills one run immediately.

```bash
curl -X POST "https://www.socialcrawl.dev/v1/monitors" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe": "prism/brand-mentions",
    "params": { "keyword": "acme" },
    "cadence": "daily",
    "webhook_url": "https://example.com/hooks/socialcrawl",
    "alert_rules": [{ "metric": "negative_share", "op": "pct_change_gt", "value": 25, "window": "1w" }]
  }'
```

## GET /v1/monitors — list your monitors

Owner-scoped, cursor-paginated.
- `status` (optional, enum: active | paused | all)
- `cursor` (optional, string)
- `limit` (optional, integer, 1–100, default 20)

```bash
curl "https://www.socialcrawl.dev/v1/monitors?status=active&limit=20" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/monitors/{id} — get one monitor

Returns the monitor (404 if not owned — never leaks existence or the webhook secret).

```bash
curl "https://www.socialcrawl.dev/v1/monitors/mon_123" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/monitors/{id}/runs — run history

Reverse-chron run history, each with its `legs[]` envelope + `alerts_fired`.
- `status` (optional, enum: ok | partial | failed | skipped)
- `from` / `to` (optional, ISO timestamps)
- `cursor` (optional, string), `limit` (optional, integer, 1–100, default 20)
- `include` (optional, enum: result) — set to `result` to include each run's full stored result envelope.

```bash
curl "https://www.socialcrawl.dev/v1/monitors/mon_123/runs?include=result" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## GET /v1/monitors/{id}/timeseries — the headline read

Projects each stored run's stable computed keys into a `{ t, metrics }` series (reads snapshots, no live API calls — costs 0 credits).
- `metric` (optional, string) — comma-separated metric keys to project (defaults to all stable computed keys).
- `from` / `to` (optional, ISO timestamps).

```bash
curl "https://www.socialcrawl.dev/v1/monitors/mon_123/timeseries?metric=negative_share,volume" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```

## PATCH /v1/monitors/{id} — pause / resume

Body: `{ "status": "paused" }` or `{ "status": "active" }`.

```bash
curl -X PATCH "https://www.socialcrawl.dev/v1/monitors/mon_123" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "status": "paused" }'
```

## DELETE /v1/monitors/{id} — delete

Unschedules and cascade-deletes the monitor's runs and webhook. Returns `204 No Content`.

```bash
curl -X DELETE "https://www.socialcrawl.dev/v1/monitors/mon_123" \
  -H "x-api-key: $SOCIALCRAWL_API_KEY"
```
