# Karan's agent skills

Private reference archive for skills installed across Claude Code, Codex, Grok, Kimi, OpenCode, Pi, and other compatible harnesses.

Start here:

- [Skill catalog](CATALOG.md) - every archived skill package, its purpose, and known upstream source.
- [Installation guide](INSTALL.md) - install one skill, install the archive, update skills, and reload harnesses.
- [Skill files](skills/) - complete skill packages. Each folder's `SKILL.md` is the source of truth.
- [Fleet contract](AGENTS.md) - Firstmate operating rules.
- [Global rules](CLAUDE.md) - standing instructions shared across projects.

## Maintenance

The catalog is generated from skill frontmatter. Sync current global skills and rebuild it with:

```bash
python3 scripts/sync_catalog.py \
  --source "$HOME/.agents/skills" \
  --destination skills \
  --lock "$HOME/.agents/.skill-lock.json" \
  --catalog CATALOG.md
```

The sync is non-destructive. It updates installed skills and preserves archive-only entries. Git history remains the recovery path for every tracked change.

Catalog count and installer count can differ. Catalog includes legacy packages, test fixtures, malformed source files, and nested packages kept for reference. `skills@latest` installs only packages that pass its current discovery and frontmatter validation.

Third-party skills remain the work of their original authors. Use the Source column in [CATALOG.md](CATALOG.md) to inspect upstream ownership before installation.
