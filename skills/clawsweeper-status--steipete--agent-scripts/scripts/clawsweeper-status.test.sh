#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

cat >"$tmpdir/gh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >>"${GH_TEST_LOG:?}"

case "$1 $2" in
  "run list")
    printf '%s\n' '[{"databaseId":11,"name":"Sweep","status":"completed","conclusion":"failure","createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/11"}]'
    ;;
  "run view")
    case "$3" in
      21)
        printf '%s\n' '[{"name":"opaque worker","status":"in_progress","conclusion":null,"steps":["Run setup-codex"]},{"name":"intake","status":"in_progress","conclusion":null,"steps":[]},{"name":"Retry failed Codex reviews","status":"in_progress","conclusion":null,"steps":[]},{"name":"Publish","status":"in_progress","conclusion":null,"steps":[]}]'
        ;;
      22)
        printf '%s\n' '[{"name":"Review commit abc","status":"queued","conclusion":null,"steps":[]}]'
        ;;
      24)
        printf '%s\n' '[{"name":"intake","status":"requested","conclusion":null,"steps":[]}]'
        ;;
      25)
        printf '%s\n' '[{"name":"Review, comment, and apply event item","status":"in_progress","conclusion":null,"steps":[]}]'
        ;;
      26)
        printf '%s\n' '[{"name":"Review shard 1","status":"in_progress","conclusion":null,"steps":[]},{"name":"Review shard 2","status":"in_progress","conclusion":null,"steps":[]}]'
        ;;
      *)
        echo "unexpected run view: $*" >&2
        exit 1
        ;;
    esac
    ;;
  "pr list")
    printf '%s\n' '[{"title":"Generated repair","url":"https://github.test/pull/7","mergedAt":"2099-01-01T00:00:00Z","mergedBy":{"login":"maintainer"},"labels":[]}]'
    ;;
  "api repos/test/target/issues/comments"*)
    if [[ "$*" == *"per_page=20"* ]]; then
      echo "github_response_too_large" >&2
      exit 1
    fi
    printf '%s\n' '[{"user":{"login":"clawsweeper"},"body":"Codex review: clean","html_url":"https://github.test/comment/8","issue_url":"https://api.github.test/issues/8"}]'
    ;;
  "api repos/test/sweeper/contents/config/automation-limits.json"*)
    printf '%s\n' '{"workers":{"max":128},"lanes":{"exact_review":{"max_concurrent":28,"target_max_concurrent":24}}}'
    ;;
  "api repos/test/sweeper/actions/runs?status=in_progress&per_page=12")
    printf '%s\n' '[{"databaseId":21,"name":"ClawSweeper review","event":"workflow_dispatch","status":"in_progress","conclusion":null,"createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/21"},{"databaseId":25,"name":"Review event item test/target#25","event":"repository_dispatch","status":"in_progress","conclusion":null,"createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/25"},{"databaseId":26,"name":"Review event items test/target#26,27 [shards=2]","event":"workflow_dispatch","status":"in_progress","conclusion":null,"createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/26"}]'
    ;;
  "api repos/test/sweeper/actions/runs?status=queued&per_page=12")
    printf '%s\n' '[{"databaseId":22,"name":"ClawSweeper review","status":"queued","conclusion":null,"createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/22"}]'
    ;;
  "api repos/test/sweeper/actions/runs?status=pending&per_page=12")
    printf '%s\n' '[{"databaseId":23,"name":"ClawSweeper review","status":"pending","conclusion":null,"createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/23"}]'
    ;;
  "api repos/test/sweeper/actions/runs?status=requested&per_page=12")
    printf '%s\n' '[{"databaseId":24,"name":"repair commit finding intake","status":"requested","conclusion":null,"createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/24"}]'
    ;;
  "api repos/test/sweeper/actions/runs?status=failure&per_page=12")
    printf '%s\n' '[{"databaseId":11,"name":"Sweep","status":"completed","conclusion":"failure","createdAt":"2099-01-01T00:00:00Z","url":"https://github.test/runs/11"}]'
    ;;
  "api repos/test/sweeper/actions/runs?status="*)
    printf '%s\n' '[]'
    ;;
  "api graphql")
    printf '%s\n' '{"data":{"pulls":{"nodes":[{"title":"Closed pull request","url":"https://github.test/pull/9","closedAt":"2099-01-01T00:00:00Z","timelineItems":{"nodes":[{"createdAt":"2099-01-01T00:00:00Z","actor":{"login":"clawsweeper"}}]}}]},"issues":{"nodes":[{"title":"Fixed issue","url":"https://github.test/issues/9","closedAt":"2099-01-01T00:00:00Z","timelineItems":{"nodes":[{"createdAt":"2099-01-01T00:00:00Z","actor":{"login":"clawsweeper"}}]}}]}}}'
    ;;
  *)
    echo "unexpected gh call: $*" >&2
    exit 1
    ;;
esac
EOF
chmod +x "$tmpdir/gh"

cat >"$tmpdir/curl" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [ "${CURL_TEST_MODE:-}" = "fail" ]; then
  exit 22
elif [ "${CURL_TEST_MODE:-}" = "absent" ]; then
  printf '%s\n' '{"pending":2,"dispatching":3,"leased":5,"target_stats":[{"target_repo":"test/other","pending":1,"dispatching":2,"leased":4}]}'
  exit 0
fi
printf '%s\n' '{"pending":2,"dispatching":3,"leased":5,"target_stats":[{"target_repo":"test/target","pending":1,"dispatching":2,"leased":4}]}'
EOF
chmod +x "$tmpdir/curl"

export GH_TEST_LOG="$tmpdir/gh.log"
PATH="$tmpdir:$PATH" "$script_dir/clawsweeper-status.sh" \
  --repo test/target \
  --clawsweeper-repo test/sweeper \
  --limit 8 \
  --run-limit 12 >"$tmpdir/output"

grep -Fq -- '- Active workflow runs: 6' "$tmpdir/output"
grep -Fq -- '- Queued/waiting workflow runs: 2' "$tmpdir/output"
grep -Fq -- '- Workflow concurrency waiters: 1' "$tmpdir/output"
grep -Fq -- '- Failed/timed-out/action-required recent runs: 1' "$tmpdir/output"
grep -Fq -- '- Active Codex jobs: 8/128 running, 2 queued' "$tmpdir/output"
grep -Fq -- '- Exact-review queue: 8/28 active, 2 pending (target test/target: 6/24 active, 1 pending)' "$tmpdir/output"
grep -Fq 'https://github.test/pull/7' "$tmpdir/output"
grep -Fq 'https://github.test/comment/8' "$tmpdir/output"
grep -Fq 'https://github.test/pull/9' "$tmpdir/output"
grep -Fq 'https://github.test/issues/9' "$tmpdir/output"
grep -Fq 'run list --repo test/sweeper --limit 12 --json' "$GH_TEST_LOG"
grep -Fq 'api repos/test/sweeper/actions/runs?status=failure&per_page=12 --jq' "$GH_TEST_LOG"
grep -Fq 'issues/comments?sort=updated&direction=desc&per_page=20' "$GH_TEST_LOG"
grep -Fq 'issues/comments?sort=updated&direction=desc&per_page=10' "$GH_TEST_LOG"
grep -Fq 'pullSearchQuery=repo:test/target is:pr is:closed is:unmerged' "$GH_TEST_LOG"
grep -Fq 'issueSearchQuery=repo:test/target is:issue is:closed' "$GH_TEST_LOG"
grep -Fq 'api repos/test/sweeper/contents/config/automation-limits.json -H Accept: application/vnd.github.raw' "$GH_TEST_LOG"
if grep -Fq 'run view 25' "$GH_TEST_LOG"; then
  echo "queue-backed exact-review workflow was not deduplicated against the queue" >&2
  exit 1
fi
grep -Fq 'run view 26' "$GH_TEST_LOG"

CURL_TEST_MODE=absent PATH="$tmpdir:$PATH" "$script_dir/clawsweeper-status.sh" \
  --repo test/target \
  --clawsweeper-repo test/sweeper \
  --limit 8 \
  --run-limit 12 >"$tmpdir/output-absent"
grep -Fq -- '- Exact-review queue: 8/28 active, 2 pending (target test/target: 0/24 active, 0 pending)' "$tmpdir/output-absent"

CURL_TEST_MODE=fail PATH="$tmpdir:$PATH" "$script_dir/clawsweeper-status.sh" \
  --repo test/target \
  --clawsweeper-repo test/sweeper \
  --limit 8 \
  --run-limit 12 >"$tmpdir/output-failed"
grep -Fq -- '- Exact-review queue: unavailable' "$tmpdir/output-failed"

if grep -Fq 'run view 23' "$GH_TEST_LOG"; then
  echo "workflow concurrency waiter was probed as a job-bearing run" >&2
  exit 1
fi
if grep -Eq 'actions/runs($| )|per_page=100|pulls\?state=closed' "$GH_TEST_LOG"; then
  echo "broad GitHub payload query detected" >&2
  exit 1
fi

echo "clawsweeper-status tests passed"
