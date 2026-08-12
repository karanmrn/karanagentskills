#!/bin/bash
set -euo pipefail

root=${1:-"$HOME/Projects"}
days=${2:-3}
format=${3:-tsv}

if [[ ! -d "$root" ]]; then
  printf 'project root not found: %s\n' "$root" >&2
  exit 2
fi
if ! [[ "$days" =~ ^[1-9][0-9]*$ ]]; then
  printf 'days must be a positive integer\n' >&2
  exit 2
fi
if [[ "$format" != tsv && "$format" != nul ]]; then
  printf 'format must be tsv or nul\n' >&2
  exit 2
fi
root=$(cd "$root" && pwd -P)

shopt -s nullglob

cwd_file=$(mktemp "${TMPDIR:-/tmp}/repo-sync-cwds.XXXXXX")
repo_file=$(mktemp "${TMPDIR:-/tmp}/repo-sync-repos.XXXXXX")
seen_file=$(mktemp "${TMPDIR:-/tmp}/repo-sync-seen.XXXXXX")
cleanup() { rm -f "$cwd_file" "$repo_file" "$seen_file"; }
trap cleanup EXIT
if ! lsof -a -u "$USER" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' > "$cwd_file"; then
  printf 'cannot inventory process working directories; refusing candidates\n' >&2
  exit 3
fi

if [[ "$format" == tsv ]]; then
  printf 'repo\tpath\tbranch\tupstream\tdirty\trecent\tactive\tgit_lock\tdecision\n'
fi

discover_repos() {
  local dir=$1
  local depth=$2
  local child name physical

  for child in "$dir"/*; do
    [[ -d "$child" ]] || continue
    name=${child##*/}
    case "$name" in
      .*|node_modules|vendor|build|dist|DerivedData) continue ;;
    esac
    if [[ -L "$child" && ! -e "$child/.git" ]]; then
      continue
    fi
    if [[ -e "$child/.git" ]]; then
      if ! physical=$(cd "$child" && pwd -P); then
        printf 'cannot resolve repository path: %s\n' "$child" >&2
        continue
      fi
      case "$physical/" in
        "$root/"*) ;;
        *)
          printf 'repository resolves outside project root; skipping: %s\n' "$child" >&2
          continue
          ;;
      esac
      if ! grep -Fqx "$physical" "$seen_file"; then
        printf '%s\n' "$physical" >> "$seen_file"
        printf '%s\0' "$physical" >> "$repo_file"
      fi
    elif (( depth < 3 )); then
      discover_repos "$child" "$((depth + 1))"
    fi
  done
}

discover_repos "$root" 0

while IFS= read -r -d '' repo; do

  branch=$(git -C "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null || printf 'DETACHED')
  if ! upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null); then
    upstream=-
  fi

  git_lock=unknown
  git_dir=$(git -C "$repo" rev-parse --absolute-git-dir 2>/dev/null || true)
  common_raw=$(git -C "$repo" rev-parse --git-common-dir 2>/dev/null || true)
  common_dir=
  if [[ -n "$common_raw" ]]; then
    if [[ "$common_raw" == /* ]]; then
      common_dir=$common_raw
    else
      common_dir=$(cd "$repo" && cd "$common_raw" 2>/dev/null && pwd -P || true)
    fi
  fi
  if [[ -n "$git_dir" && -n "$common_dir" ]]; then
    if lock_path=$(find "$git_dir" "$common_dir" -name '*.lock' -print -quit 2>/dev/null); then
      git_lock=no
      [[ -n "$lock_path" ]] && git_lock=yes
    fi
  fi

  dirty=unknown
  if [[ "$git_lock" == no ]]; then
    if state=$(GIT_OPTIONAL_LOCKS=0 git -C "$repo" status --porcelain=v2 --untracked-files=normal 2>/dev/null); then
      dirty=no
      [[ -n "$state" ]] && dirty=yes
    fi
  fi

  # Machine updater ignores recency; keep the expensive signal for human audits only.
  recent=not-scanned
  if [[ "$format" == tsv ]]; then
    recent=unknown
    if recent_path=$(find "$repo" \( -path '*/.git' -o -path '*/node_modules' \) -prune -o -type f -mtime "-$days" -print -quit 2>/dev/null); then
      recent=no
      [[ -n "$recent_path" ]] && recent=yes
    fi
  fi

  active=no
  while IFS= read -r cwd; do
    case "$cwd/" in
      "$repo/"*) active=yes; break ;;
    esac
  done < "$cwd_file"

  decision=candidate
  if [[ "$git_lock" == yes ]]; then
    decision=skip-git-lock
  elif [[ "$git_lock" == unknown ]]; then
    decision=skip-lock-error
  elif [[ "$active" == yes ]]; then
    decision=skip-active
  elif [[ "$dirty" == unknown ]]; then
    decision=skip-status-error
  elif [[ "$branch" == DETACHED ]]; then
    decision=escalate-detached
  elif [[ "$upstream" == - ]]; then
    decision=escalate-no-upstream
  fi

  if [[ "$format" == nul ]]; then
    printf '%s\0' repo "$repo" "$branch" "$upstream" "$dirty" "$recent" "$active" "$git_lock" "$decision"
  else
    printf 'repo\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$repo" "$branch" "$upstream" "$dirty" "$recent" "$active" "$git_lock" "$decision"
  fi
done < "$repo_file"
