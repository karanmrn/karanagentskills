Complete the GitHub issue below in this isolated worktree. Do not push branches or open pull requests.

GitHub issue:

{issue_url}

Another agent explored the repository and produced this plan:

{plan}

Instructions:

1. Use the `gh` CLI to inspect the issue and any relevant comments yourself (read-only is fine; PR creation is not).
2. Use the plan as guidance, but verify it independently.
3. Make the necessary code changes in the current worktree.
4. Run appropriate tests or checks when possible.
5. Create exactly one local commit that addresses the issue. Do not push, do not create a PR, do not run `gh pr create`, and do not interact with any `upstream` remote.
6. In your final response, return ONLY the commit SHA (the full 40-character hex string, or a short SHA such as `abc1234`). Do not include prose, markdown, a summary, or anything else.

The local-commit benchmark mode evaluates the committed artifact directly (diff, commit message, tests, worktree state). No external side effects are permitted.
