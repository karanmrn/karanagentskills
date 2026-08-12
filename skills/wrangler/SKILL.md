---
name: wrangler
description: "Wrangler CLI: Workers, KV, tail, deploy, account routing."
---

# Wrangler

Use for Cloudflare Wrangler CLI work: deploys, tails, KV/R2/D1/Queues/Workers, secrets, bindings, and account routing.

## Defaults

- Retrieval first for flags/config: `wrangler --help`, subcommand `--help`, local `node_modules/wrangler/config-schema.json`, then Cloudflare docs.
- Prefer repo wrapper: `npm exec --yes --package wrangler -- wrangler ...` unless repo has its own script.
- `wrangler whoami` before account-sensitive work.
- ReleaseBar prod account: `Steipete@gmail.com's Account` / `de09342a728de2c25c85cc6b34d68739`.
- OpenClaw projects: use OpenClaw account / `91b59577e757131d68d55a471fe32aca`. Ask if unsure.

## Pitfalls

- Do not invent flags from memory. Wrangler 4 removed/changed some old flags; confirm with `--help`.
- `wrangler kv key list` has no `--limit`; use `--prefix` and filter locally.
- Run Wrangler KV/list/get/admin reads serially when workerd/local storage starts up; parallel runs can hit SQLite `SQLITE_BUSY`.
- `wrangler tail --sampling-rate` must be `>0` and `<1`; use `0.999` for near-full sampling, not `1`.
- Stop tails you start. Use a PTY when interactive stop matters; otherwise kill the exact `wrangler tail <worker>` process.
- Never print secrets. Query exact secret names only; do not dump env.

## Quick Commands

```bash
npm exec --yes --package wrangler -- wrangler whoami
npm exec --yes --package wrangler -- wrangler deploy
npm exec --yes --package wrangler -- wrangler tail <worker> --format json --sampling-rate 0.999 --search '<term>'
npm exec --yes --package wrangler -- wrangler kv key list --namespace-id <id> --prefix '<prefix>'
npm exec --yes --package wrangler -- wrangler kv key get '<key>' --namespace-id <id>
```

## Account Check

For repo config, read `wrangler.toml` / `wrangler.json(c)` before commands. If config account and intended product disagree, stop and ask.
