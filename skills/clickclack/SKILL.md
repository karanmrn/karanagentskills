---
name: clickclack
description: "ClickClack ops: chat app, Cloudflare Workers deploy, DNS/docs/app, container rollout."
---

# ClickClack

Use this for ClickClack product/runtime ops, deploys, hosted app checks, and domain questions.

## What

- Repo: `~/Projects/clickclack` / `https://github.com/openclaw/clickclack`
- Product: self-hostable Slack-style chat for OpenClaw/community/agent workflows.
- Surfaces:
  - `https://clickclack.chat` product site (Cloudflare Worker custom domain)
  - `https://www.clickclack.chat` (Worker custom domain, same worker)
  - `https://app.clickclack.chat` hosted app (Worker custom domain)
  - `https://docs.clickclack.chat` GitHub Pages docs from `docs/`

## Prod (Cloudflare, since 2026-07-05)

- Everything is one Cloudflare Worker `clickclack` in the OpenClaw account (`91b59577e757131d68d55a471fe32aca`) fronting a Cloudflare Container.
- Worker + container config: `wrangler.jsonc` (routes are declarative `custom_domain` entries).
- Container: Go binary + embedded SPA from `Dockerfile.cloudflare`; data in Supabase Postgres (`CLICKCLACK_DB` secret) and R2 uploads (`clickclack-uploads`).
- Zone `clickclack.chat` id `e7f93ba1ec24d75ce60c468bbaba5cb5` (OpenClaw account). `docs` CNAME → `openclaw.github.io` stays DNS-only.
- 1Password (OpenClaw vault): "Cloudflare ClickClack deploy token" (`api_token` field, workers-scoped; no DNS edit), "Cloudflare ClickClack R2 uploads".
- Legacy Hetzner box `clickclack-prod-01` (157.90.237.80) no longer serves any DNS; decommission when confident. Old runbook in git history of this file.

## Deploy

1. `cd ~/Projects/clickclack && git pull --ff-only`
2. Docker must run (OrbStack: `open -a OrbStack`).
3. `pnpm deploy:cloudflare` (auth: `wrangler login` OAuth or the 1Password deploy token as `CLOUDFLARE_API_TOKEN`).
4. **Rollout gotcha:** the running container instance is NOT replaced while it has traffic; `sleepAfter=10m` never fires on a public site. Bump `CLICKCLACK_CONTAINER_NAME` in `wrangler.jsonc` (dated, e.g. `prod-YYYYMMDD-open-org`) and redeploy to force a fresh instance on the new image. Container is stateless (Postgres/R2), so the swap is safe.
5. Commit the `wrangler.jsonc` bump.

## Verify

- `curl -s https://clickclack.chat/ | grep -oE 'entry/app\.[A-Za-z0-9_-]+\.js'` — hash must match the freshly deployed build (compare against `https://clickclack.services-91b.workers.dev`).
- Same check for `https://app.clickclack.chat` and `https://www.clickclack.chat`.
- `pnpm exec wrangler containers info a03b3158-bcfd-4962-9a86-e75489f4e803` — health + image digest.
- `curl -I https://docs.clickclack.chat`

## Guardrails

- Do not print OAuth secrets or magic tokens.
- The deploy token has no DNS scope; DNS record changes need the dashboard or a Zone.DNS token.
- Keep deploys from clean git checkouts, not dirty working trees.
