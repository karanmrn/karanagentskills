#!/bin/bash
set -u -o pipefail

root=${1:-"$HOME/Projects"}
days=${2:-3}
script_dir=$(cd "$(dirname "$0")" && pwd -P)
audit="$script_dir/repo-sync-audit.sh"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/repo-sync-update.XXXXXX") || exit 1
cleanup() { rm -rf "$tmp"; }
on_int() { trap - EXIT INT TERM; cleanup; exit 130; }
on_term() { trap - EXIT INT TERM; cleanup; exit 143; }
trap cleanup EXIT
trap on_int INT
trap on_term TERM

run_with_timeout() {
  local seconds=$1
  shift
  perl -MPOSIX -e '
    my $seconds = shift @ARGV;
    my $pid = fork();
    exit 125 unless defined $pid;
    if ($pid == 0) {
      POSIX::setpgid(0, 0);
      exec @ARGV;
      exit 127;
    }
    sub stop_group {
      my ($code) = @_;
      kill "TERM", -$pid;
      sleep 2;
      kill "KILL", -$pid;
      waitpid($pid, 0);
      exit $code;
    }
    $SIG{ALRM} = sub { stop_group(124) };
    $SIG{INT} = sub { stop_group(130) };
    $SIG{TERM} = sub { stop_group(143) };
    alarm $seconds;
    waitpid($pid, 0);
    alarm 0;
    my $wait = $?;
    exit(128 + POSIX::WTERMSIG($wait)) if POSIX::WIFSIGNALED($wait);
    exit(POSIX::WEXITSTATUS($wait)) if POSIX::WIFEXITED($wait);
    exit 125;
  ' "$seconds" "$@"
}

check_git_locks() {
  local git_dir=$1
  local common_dir=$2
  local output=$3
  if ! find "$git_dir" "$common_dir" -name '*.lock' -print -quit >"$output" 2>/dev/null; then
    return 2
  fi
  [[ -s "$output" ]]
}

has_symlink_parent() {
  local repo=$1
  local path=$2
  while [[ "$path" == */* ]]; do
    path=${path%/*}
    [[ -L "$repo/$path" ]] && return 0
  done
  return 1
}

collect_local_paths() {
  local repo=$1
  local output=$2
  local upstream=$3
  local collisions=$4
  : >"$collisions"
  if ! git -C "$repo" diff --name-only -z HEAD >"$output.tracked" ||
    ! git -C "$repo" ls-files --others --exclude-standard -z >"$output.untracked" ||
    ! git -C "$repo" ls-files -v -z >"$output.index-flags"; then
    return 1
  fi
  while IFS= read -r -d '' record; do
    tag=${record%% *}
    if [[ "$tag" == S || "$tag" =~ ^[a-z]$ ]]; then
      printf '%s\0' "${record:2}" >>"$collisions"
    fi
  done <"$output.index-flags"
  cat "$output.tracked" "$output.untracked" >"$output"
  if [[ -s "$collisions" ]]; then
    return 0
  fi
  # Clean visible state is protected by merge --no-overwrite-ignore below.
  if [[ ! -s "$output.tracked" && ! -s "$output.untracked" ]]; then
    return 0
  fi
  if ! git -C "$repo" diff --name-only -z "HEAD..$upstream" >"$output.incoming"; then
    return 1
  fi
  : >"$output.existing-incoming"
  while IFS= read -r -d '' path; do
    check=$path
    while [[ -n "$check" ]]; do
      if [[ -e "$repo/$check" || -L "$repo/$check" ]] &&
        ! has_symlink_parent "$repo" "$check"; then
        printf '%s\0' "$check" >>"$output.existing-incoming"
      fi
      [[ "$check" == */* ]] || break
      check=${check%/*}
    done
  done <"$output.incoming"

  ignore_rc=0
  git -C "$repo" check-ignore -z --stdin \
    <"$output.existing-incoming" >"$output.ignored-incoming" || ignore_rc=$?
  if (( ignore_rc > 1 )); then
    return 1
  fi
  cat "$output.ignored-incoming" >>"$collisions"
}

snapshot_local_content() {
  local repo=$1
  local paths=$2
  local output=$3
  perl -MDigest::SHA -e '
    use strict;
    use warnings;
    my ($repo, $paths) = @ARGV;
    open my $list, "<:raw", $paths or exit 2;
    local $/ = "\0";
    while (defined(my $path = <$list>)) {
      chop $path;
      my $full = "$repo/$path";
      print $path, "\0";
      if (-l $full) {
        my $target = readlink $full;
        exit 2 unless defined $target;
        print "link\0", Digest::SHA::sha256_hex("$target\n"), "\0";
      } elsif (-f $full) {
        open my $content, "<:raw", $full or exit 2;
        my $sha = Digest::SHA->new(256);
        $sha->addfile($content);
        close $content or exit 2;
        my $digest = $sha->hexdigest;
        $digest = "\\$digest" if $full =~ /[\\\n]/;
        print "file\0", $digest, "\0";
      } elsif (-d $full) {
        print "directory\0";
      } else {
        print "missing\0";
      }
    }
    close $list or exit 2;
    close STDOUT or exit 2;
  ' "$repo" "$paths" >"$output"
}

if ! "$audit" "$root" "$days" nul >"$tmp/audit.nul"; then
  printf 'sync-error\taudit-failed\n' >&2
  exit 1
fi

printf 'sync\tpath\tresult\tdetail\n'
while IFS= read -r -d '' kind &&
  IFS= read -r -d '' repo &&
  IFS= read -r -d '' branch &&
  IFS= read -r -d '' upstream &&
  IFS= read -r -d '' dirty &&
  IFS= read -r -d '' recent &&
  IFS= read -r -d '' active &&
  IFS= read -r -d '' git_lock &&
  IFS= read -r -d '' decision; do
  [[ "$kind" == repo && "$decision" == candidate ]] || continue

  if ! lsof -a -u "$USER" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' >"$tmp/cwds"; then
    printf 'sync\t%s\tskipped\tactivity-audit-failed\n' "$repo"
    continue
  fi
  if awk -v repo="$repo/" 'index($0 "/", repo) == 1 { found=1 } END { exit !found }' "$tmp/cwds"; then
    printf 'sync\t%s\tskipped\tactive\n' "$repo"
    continue
  fi
  git_dir=$(git -C "$repo" rev-parse --absolute-git-dir)
  common_raw=$(git -C "$repo" rev-parse --git-common-dir)
  if [[ "$common_raw" == /* ]]; then
    common_dir=$common_raw
  else
    common_dir=$(cd "$repo" && cd "$common_raw" && pwd -P)
  fi
  check_git_locks "$git_dir" "$common_dir" "$tmp/lock"
  lock_rc=$?
  if [[ "$lock_rc" == 0 ]]; then
    printf 'sync\t%s\tskipped\tgit-lock\n' "$repo"
    continue
  elif [[ "$lock_rc" == 2 ]]; then
    printf 'sync\t%s\tskipped\tlock-audit-failed\n' "$repo"
    continue
  fi
  audited_branch=$(git -C "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null || true)
  audited_upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
  if [[ -z "$audited_branch" || -z "$audited_upstream" ]]; then
    printf 'sync\t%s\tescalated\tmissing-branch-or-upstream\n' "$repo"
    continue
  fi

  run_with_timeout 300 env GIT_TERMINAL_PROMPT=0 \
    GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3' \
    git -C "$repo" fetch --prune
  fetch_rc=$?
  if [[ "$fetch_rc" != 0 ]]; then
    [[ "$fetch_rc" == 124 ]] && detail=fetch-timeout || detail=fetch-failed
    printf 'sync\t%s\tpending\t%s\n' "$repo" "$detail"
    continue
  fi

  if ! lsof -a -u "$USER" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' >"$tmp/cwds"; then
    printf 'sync\t%s\tskipped\tactivity-audit-failed-after-fetch\n' "$repo"
    continue
  fi
  if awk -v repo="$repo/" 'index($0 "/", repo) == 1 { found=1 } END { exit !found }' "$tmp/cwds"; then
    printf 'sync\t%s\tskipped\tbecame-active\n' "$repo"
    continue
  fi
  check_git_locks "$git_dir" "$common_dir" "$tmp/lock"
  lock_rc=$?
  if [[ "$lock_rc" == 0 ]]; then
    printf 'sync\t%s\tskipped\tgit-lock-after-fetch\n' "$repo"
    continue
  elif [[ "$lock_rc" == 2 ]]; then
    printf 'sync\t%s\tskipped\tlock-audit-failed-after-fetch\n' "$repo"
    continue
  fi
  branch=$(git -C "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null || true)
  upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
  if [[ "$branch" != "$audited_branch" || "$upstream" != "$audited_upstream" ]]; then
    printf 'sync\t%s\tskipped\tbranch-or-upstream-changed\n' "$repo"
    continue
  fi
  if ! counts=$(git -C "$repo" rev-list --left-right --count HEAD...@{upstream}) ||
    ! read -r ahead behind <<<"$counts" || [[ ! "$ahead" =~ ^[0-9]+$ || ! "$behind" =~ ^[0-9]+$ ]]; then
    printf 'sync\t%s\tskipped\trev-list-failed\n' "$repo"
    continue
  fi
  if [[ "$ahead" != 0 ]]; then
    printf 'sync\t%s\tescalated\tahead=%s behind=%s\n' "$repo" "$ahead" "$behind"
    continue
  fi
  if [[ "$behind" == 0 ]]; then
    printf 'sync\t%s\tcurrent\t%s\n' "$repo" "$branch"
    continue
  fi

  pre_head=$(git -C "$repo" rev-parse HEAD)
  pre_state=$(GIT_OPTIONAL_LOCKS=0 git -C "$repo" status --porcelain=v2 --untracked-files=normal)
  if ! collect_local_paths "$repo" "$tmp/local-paths" "$upstream" "$tmp/ignored-collisions"; then
    printf 'sync\t%s\tskipped\tlocal-path-audit-failed\n' "$repo"
    continue
  fi
  if [[ -s "$tmp/ignored-collisions" ]]; then
    printf 'sync\t%s\tskipped\tignored-local-collision\n' "$repo"
    continue
  fi
  if ! snapshot_local_content "$repo" "$tmp/local-paths" "$tmp/local-before"; then
    printf 'sync\t%s\tskipped\tlocal-snapshot-failed\n' "$repo"
    continue
  fi
  if ! lsof -a -u "$USER" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' >"$tmp/cwds"; then
    printf 'sync\t%s\tskipped\tactivity-audit-failed-at-merge\n' "$repo"
    continue
  fi
  if awk -v repo="$repo/" 'index($0 "/", repo) == 1 { found=1 } END { exit !found }' "$tmp/cwds"; then
    printf 'sync\t%s\tskipped\tbecame-active-at-merge\n' "$repo"
    continue
  fi
  check_git_locks "$git_dir" "$common_dir" "$tmp/lock"
  lock_rc=$?
  if [[ "$lock_rc" == 0 ]]; then
    printf 'sync\t%s\tskipped\tgit-lock-at-merge\n' "$repo"
    continue
  elif [[ "$lock_rc" == 2 ]]; then
    printf 'sync\t%s\tskipped\tlock-audit-failed-at-merge\n' "$repo"
    continue
  fi
  current_branch=$(git -C "$repo" symbolic-ref --quiet --short HEAD 2>/dev/null || true)
  current_upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
  current_head=$(git -C "$repo" rev-parse HEAD 2>/dev/null || true)
  current_state=$(GIT_OPTIONAL_LOCKS=0 git -C "$repo" status --porcelain=v2 --untracked-files=normal)
  if ! snapshot_local_content "$repo" "$tmp/local-paths" "$tmp/local-at-merge"; then
    printf 'sync\t%s\tskipped\tlocal-resnapshot-failed\n' "$repo"
    continue
  fi
  if [[ "$current_branch" != "$branch" || "$current_upstream" != "$upstream" || \
    "$current_head" != "$pre_head" || "$current_state" != "$pre_state" ]] || \
    ! cmp -s "$tmp/local-before" "$tmp/local-at-merge"; then
    printf 'sync\t%s\tskipped\tstate-changed-at-merge\n' "$repo"
    continue
  fi
  if LC_ALL=C git -C "$repo" -c core.hooksPath=/dev/null merge --ff-only --no-autostash --no-overwrite-ignore "$upstream" \
    >"$tmp/merge-output" 2>&1; then
    cat "$tmp/merge-output"
    expected=$(git -C "$repo" rev-parse "$upstream")
    post_head=$(git -C "$repo" rev-parse HEAD)
    if ! snapshot_local_content "$repo" "$tmp/local-paths" "$tmp/local-after"; then
      printf 'sync\t%s\terror\tpost-merge-snapshot-failed\n' "$repo"
      touch "$tmp/errors"
      continue
    fi
    if [[ "$post_head" != "$expected" ]] || ! git -C "$repo" diff --diff-filter=U --quiet || \
      ! cmp -s "$tmp/local-before" "$tmp/local-after"; then
      printf 'sync\t%s\terror\tpost-merge-verification\n' "$repo"
      touch "$tmp/errors"
      continue
    fi
    printf 'sync\t%s\tpulled\tcommits=%s dirty-before=%s\n' "$repo" "$behind" "$([[ -n "$pre_state" ]] && printf yes || printf no)"
    continue
  fi

  post_head=$(git -C "$repo" rev-parse HEAD)
  post_state=$(GIT_OPTIONAL_LOCKS=0 git -C "$repo" status --porcelain=v2 --untracked-files=normal)
  if [[ "$post_head" != "$pre_head" || "$post_state" != "$pre_state" ]] || ! git -C "$repo" diff --diff-filter=U --quiet; then
    printf 'sync\t%s\terror\trefusal-changed-state\n' "$repo"
    touch "$tmp/errors"
    continue
  fi
  if grep -Eqi 'would be overwritten by (merge|checkout)|untracked working tree files would be overwritten|not uptodate|refusing to lose untracked' "$tmp/merge-output"; then
    printf 'sync\t%s\tskipped\tlocal-overlap\n' "$repo"
  else
    printf 'sync\t%s\tpending\tmerge-failed\n' "$repo"
    touch "$tmp/errors"
  fi
done <"$tmp/audit.nul"

[[ ! -e "$tmp/errors" ]]
