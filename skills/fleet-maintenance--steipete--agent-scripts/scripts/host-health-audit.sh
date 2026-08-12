#!/bin/bash
set -u -o pipefail

threshold_gib=${1:-30}
case "$threshold_gib" in
  ''|*[!0-9]*)
    printf 'usage: %s [memory-threshold-gib]\n' "$0" >&2
    exit 2
    ;;
esac

threshold_kib=$((threshold_gib * 1024 * 1024))
tmp=$(mktemp -d /tmp/fleet-ownership.XXXXXX) || exit 1
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT INT TERM

printf 'memory-threshold\t%s GiB\n' "$threshold_gib"
if ! ps -axo pid=,rss=,user=,comm= >"$tmp/processes" || ! test -s "$tmp/processes"; then
  printf 'health-audit\terror=process-inventory\n' >&2
  exit 1
fi
awk -v threshold="$threshold_kib" '
  $2 > threshold {
    pid = $1
    rss = $2
    user = $3
    $1 = $2 = $3 = ""
    sub(/^[[:space:]]+/, "")
    printf "memory-over-limit\tpid=%s\trss_gib=%.2f\tuser=%s\tcommand=%s\n",
      pid, rss / 1024 / 1024, user, $0
    found = 1
  }
  END { if (!found) print "memory-over-limit\tnone" }
' "$tmp/processes"

if ! command -v brew >/dev/null 2>&1; then
  for brew_candidate in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if test -x "$brew_candidate"; then
      PATH="$(dirname "$brew_candidate"):$PATH"
      export PATH
      break
    fi
  done
fi

command -v brew >/dev/null 2>&1 || {
  printf 'ownership-audit\thomebrew-absent\n'
  exit 0
}

if ! prefix=$(brew --prefix); then
  printf 'ownership-audit\terror=homebrew-prefix\n' >&2
  exit 1
fi

if ! brew list --formula >"$tmp/formulae.raw" 2>"$tmp/formulae.err"; then
  printf 'ownership-audit\terror=formula-inventory\n' >&2
  exit 1
fi
if ! brew list --cask >"$tmp/casks.raw" 2>"$tmp/casks.err"; then
  printf 'ownership-audit\terror=cask-inventory\n' >&2
  exit 1
fi
sort -u "$tmp/formulae.raw" >"$tmp/formulae"
sort -u "$tmp/casks.raw" >"$tmp/casks"
comm -12 "$tmp/formulae" "$tmp/casks" | while IFS= read -r name; do
  test -n "$name" && printf 'ownership-candidate\tformula-cask\t%s\n' "$name"
done

if ! find "$prefix/bin" -maxdepth 1 \( -type f -o -type l \) -print 2>"$tmp/brew-bin-find.err" |
  while IFS= read -r path; do
    real=$(realpath "$path" 2>/dev/null || printf '%s' "$path")
    case "$real" in
      "$prefix"/Cellar/*)
        owner=${real#"$prefix"/Cellar/}
        owner=${owner%%/*}
        printf '%s\t%s\t%s\n' "$(basename "$path")" "$owner" "$path"
        ;;
    esac
  done | sort -u >"$tmp/brew-bins"; then
  printf 'ownership-audit\terror=homebrew-bin-inventory\n' >&2
  exit 1
fi

app_roots=(/Applications)
test ! -d "$HOME/Applications" || app_roots+=("$HOME/Applications")
if ! find "${app_roots[@]}" -maxdepth 7 -type f -perm -111 \
  \( -path '*/Contents/MacOS/*' -o -path '*/Contents/Resources/*' \) \
  -print 2>"$tmp/app-bin-find.err" >"$tmp/app-bins"; then
  printf 'ownership-audit\terror=app-bin-inventory\n' >&2
  exit 1
fi
awk -F '\t' '
  FILENAME == ARGV[1] {
    formula[$1] = $2
    brew_path[$1] = $3
    next
  }
  {
    app_path = $0
    name = app_path
    sub(/^.*\//, "", name)
    if (name in formula) {
      printf "ownership-candidate\tformula-app-cli\tname=%s\tformula=%s\tbrew=%s\tapp=%s\n",
        name, formula[name], brew_path[name], app_path
    }
  }
' "$tmp/brew-bins" "$tmp/app-bins"

if command -v jq >/dev/null 2>&1; then
  if ! brew services list --json >"$tmp/services.json" 2>"$tmp/services.err"; then
    printf 'ownership-audit\terror=service-inventory\n' >&2
    exit 1
  fi
  if ! jq -r '.[] | select(.status == "error") | [.name, (.exit_code // "unknown"), (.file // "unknown")] | @tsv' "$tmp/services.json" >"$tmp/failed-services"; then
    printf 'ownership-audit\terror=service-json\n' >&2
    exit 1
  fi
  while IFS=$'\t' read -r name exit_code file; do
    printf 'service-failed\tname=%s\texit=%s\tfile=%s\n' "$name" "$exit_code" "$file"
    if pgrep -il "$name" >"$tmp/matching-processes" 2>"$tmp/pgrep.err"; then
      while IFS= read -r process; do
        test -n "$process" && printf 'ownership-candidate\tfailed-service-process\tservice=%s\tprocess=%s\n' "$name" "$process"
      done <"$tmp/matching-processes"
    else
      pgrep_status=$?
      if test "$pgrep_status" -ne 1; then
        printf 'ownership-audit\terror=process-inventory\tservice=%s\n' "$name" >&2
        exit 1
      fi
    fi
  done <"$tmp/failed-services"
else
  if ! brew services list >"$tmp/services" 2>"$tmp/services.err"; then
    printf 'ownership-audit\terror=service-inventory\n' >&2
    exit 1
  fi
  awk '$2 == "error" { print "service-failed\tname=" $1 "\texit=" $3 }' "$tmp/services"
fi
