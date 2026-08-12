---
name: mac-maintenance
description: "Mac upkeep: brew update/upgrade, pull clean repos, empty Trash."
---

# Mac Maintenance

Use when Peter asks for Mac cleanup, maintenance, or package/repo refresh.

## Run

1. Homebrew:

```bash
brew update && brew upgrade
```

2. Repos under `~/Projects`:

```bash
for repo in ~/Projects/*/.git; do
  dir=${repo:h}
  git -C "$dir" status --short --branch
  git -C "$dir" pull --ff-only
done
```

Skip dirty repos unless Peter explicitly asked to handle them. Report skipped paths.

3. Empty Trash:

```bash
osascript -e 'tell application "Finder" to empty trash'
```

4. Finish with terse counts:

- brew: upgraded / already current
- repos: pulled / skipped / failed
- trash: emptied / failed
