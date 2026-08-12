# Batch Corral launches

## Purpose

Use the helper's `batch` command to launch multiple independent Corral tasks. It starts separate native `corral launch` processes; Corral's own cross-process locks and SQLite transactions remain authoritative.

Batch launch is state-changing. Dry-run and review every entry first.

## JSON format

The file must contain a non-empty JSON array. Every item requires `repo` and `task`.

```json
[
  {
    "repo": "<repository-checkout>",
    "task": "Investigate authentication",
    "preset": "pi",
    "priority": 2,
    "prompt": "Inspect the authentication flow and report the likely cause.",
    "no_focus": true,
    "json": true
  },
  {
    "repo": "<repository-checkout>",
    "task": "Review database migrations",
    "agent": "pi",
    "base": "main",
    "prompt_file": "prompts/review-migrations.md",
    "worktree_path": "<new-worktree-destination>",
    "no_focus": true
  }
]
```

Relative `prompt_file` paths are resolved relative to the JSON file. Repository and worktree paths are resolved normally by the helper.

## Entry fields

| Field | Type | Meaning |
| --- | --- | --- |
| `repo` | string, required | Source repository checkout. |
| `task` | string, required | Unique Corral task title, 1-80 characters. |
| `preset` | string | Exact Corral preset. If absent, helper defaults can apply. |
| `agent` | string | Select the only preset for this kind when `preset` is absent. Defaults to Pi. |
| `priority` | integer 1-4 | Task priority. |
| `base` | string | Git base ref; otherwise preset default. |
| `prompt` | string | Per-task prompt. Mutually exclusive with `prompt_file`. |
| `prompt_file` | string | UTF-8 prompt file path. |
| `worktree_path` | string | Exact new worktree destination. |
| `allow_dirty` | boolean | Proceed without including dirty primary changes. Requires explicit user approval. |
| `focus` | boolean | Focus the new workspace. |
| `no_focus` | boolean | Avoid stealing focus. Do not combine with `focus`. |
| `json` | boolean | Ask native Corral for a final JSON task record. |
| `mock_state` | string | Smoke-test only. Never include in a real batch. |

Unknown fields are rejected to catch typos.

## Command defaults

The batch command can provide defaults that entries override:

```bash
python3 scripts/corral_agents.py batch \
  --session <session> \
  --file <tasks.json> \
  --agent pi \
  --priority 3 \
  --base main \
  --no-focus \
  --parallel 3 \
  --dry-run
```

Supported command defaults are `--preset`, `--agent`, `--priority`, `--base`, `--allow-dirty`, `--focus`/`--no-focus`, and `--json`.

After reviewing the dry-run, repeat without `--dry-run`. Add `--summary-json` for a final non-sensitive return-code summary.

## Concurrency behavior

The helper defaults to three worker processes. Native Corral independently limits its full preparation pipeline to three concurrent jobs using cross-process file locks. This protects the machine from simultaneous dependency installs and builds.

Increasing `--parallel` above three normally provides no throughput benefit: extra native launchers wait for a Corral slot. Values from 1 through 32 are accepted for controlled experiments.

Each task receives a UUID-based task ID and branch suffix. SQLite uses WAL mode, a busy timeout, and immediate transactions, so concurrent task writes are supported.

## Output and failure behavior

The helper captures each native process's output, prints it when that process finishes, and returns nonzero if any launch failed. All submitted items are allowed to finish; one failure does not terminate already-running sibling launches.

A failed Corral launch can leave a failed task and worktree for inspection. This is intentional. Do not clean successful or failed worktrees automatically after a partial batch failure.

After the batch, verify each exact title:

```bash
python3 scripts/corral_agents.py status \
  --session <session> \
  --task "<exact task title>" \
  --live
```

If any item failed:

1. Record which entries succeeded before retrying.
2. Inspect the failed task state and worktree.
3. Fix its preset, repository, credentials, or runtime issue.
4. Remove successful entries from the batch file.
5. Dry-run only the intended replacements.

Never rerun the whole batch blindly; that creates duplicate tasks and worktrees.
