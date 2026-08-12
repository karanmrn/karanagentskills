---
name: pnpm-not-found
description: Fix "pnpm command not found" errors by enabling corepack. Use when pnpm cannot be found, corepack errors appear, or package manager is missing.
---

# pnpm Not Found Fix

When you encounter errors like `pnpm: command not found` or `pnpm: not found`, fix by running:

```sh
corepack enable
```

Do this without asking the user first - just enable corepack and retry.
