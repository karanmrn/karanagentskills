# Install and update skills

This repository is private. Authenticate GitHub access before installing from it:

```bash
gh auth login
gh auth setup-git
```

## Install one archived skill

Copy the exact folder name from [CATALOG.md](CATALOG.md), then run:

```bash
npx -y skills@latest add \
  "https://github.com/karanmrn/karanagentskills/tree/master/skills/<folder-name>" \
  -g --all
```

When the catalog provides an upstream source, prefer that source. It gives clearer provenance and cleaner updates:

```bash
npx -y skills@latest add <owner>/<repository> \
  -g --agent '*' --skill <skill-name> -y
```

## Install all valid skills from this archive

The archive is large. Install everything only when you need a full fleet mirror:

```bash
npx -y skills@latest add karanmrn/karanagentskills -g --all --full-depth
```

Installer scans archive and skips packages that fail its current validation. Warnings identify legacy, malformed, or fixture packages that remain in catalog for reference.

For daily work, install a small relevant set. A large catalog increases trigger overlap and can introduce conflicting instructions.

## Project installation

Omit `-g` to install into the current repository:

```bash
npx -y skills@latest add <owner>/<repository> \
  --agent '*' --skill <skill-name> -y
```

Project skills override or supplement global behavior for that repository. Use them for product language, domain rules, architecture, and design-system constraints.

## Update installed skills

Update global skills:

```bash
npx -y skills@latest update -g -y
```

Update skills tracked by the current project:

```bash
npx -y skills@latest update -p -y
```

The updater does not remove skills deleted upstream during a non-interactive update. Review those entries before deleting them.

## Load newly installed skills

No computer restart is needed.

- New Codex task or chat: recommended.
- Existing harness window: restart that harness when it does not refresh its skill index automatically.
- Existing running task: do not assume hot loading. Its skill catalog can be fixed at task start.

Eve and PromptScript do not support global skill installation. Other supported harnesses either read `~/.agents/skills` directly or receive links to that shared registry.

## Security

Skills run with agent permissions. Before use:

1. Inspect the source repository and `SKILL.md`.
2. Review installer security findings.
3. Avoid broad credentials and unnecessary tool access.
4. Pin project-specific rules locally.
5. Keep Git history so changes remain reviewable and reversible.
