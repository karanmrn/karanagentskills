---
name: clawsweeper-status
description: "ClawSweeper status: URLs, workflow health, active workers, ops snapshot."
---

# ClawSweeper Status

## Quick Start

Run the bundled status script first:

```bash
/Users/steipete/Projects/agent-scripts/skills/clawsweeper-status/scripts/clawsweeper-status.sh
```

Useful options:

```bash
# Last 10 hours for the default target repo, openclaw/openclaw
/Users/steipete/Projects/agent-scripts/skills/clawsweeper-status/scripts/clawsweeper-status.sh --hours 10

# A different target repo
/Users/steipete/Projects/agent-scripts/skills/clawsweeper-status/scripts/clawsweeper-status.sh --repo openclaw/clawhub

# More rows per activity section
/Users/steipete/Projects/agent-scripts/skills/clawsweeper-status/scripts/clawsweeper-status.sh --limit 15
```

## Output Contract

Report these sections concisely:

- `Workers`: workflow state, Codex jobs against configured capacity, exact-review queue and target occupancy, and active workflow groups.
- `Recently merged`: merged PR URLs plus one-line titles.
- `Recently reviewed`: ClawSweeper/Codex review comment URLs plus one-line comment summary.
- `Recently commented`: other recent ClawSweeper comment URLs plus one-line comment summary.
- `Recently closed`: closed issue/PR URLs plus one-line titles.

If the script returns no rows for a section, say `none found in window`.

## Efficient Data Sources

Prefer the script because it uses bounded API calls:

- field-bounded Actions run queries and bounded active-job probes from `openclaw/clawsweeper`;
- the small automation-limits config and exact-review queue status endpoint for capacity context;
- recent issue comments for review/comment URLs;
- a field-bounded closed-item search for close URLs and actors;
- field-bounded recent merged PRs.

Do not browse the web for these checks. Use `gh` directly.

## Interpretation

- Cancelled repository-dispatch review runs are usually expected supersession when a newer event for the same item arrives.
- Count Codex usage from actual in-progress/queued jobs; use setup-action steps plus known lane names to identify Codex work.
- Treat `pending` workflow runs as concurrency waiters, not queued Codex jobs.
- Treat stale worker counts cautiously; compare the status-filtered `gh run list` results with the default recent-run list when numbers disagree.
- Use full GitHub URLs in the final answer.
