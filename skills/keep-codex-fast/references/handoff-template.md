# Codex Handoff Template

Use this before archiving an important active repo chat. The goal is to let a fresh Codex thread continue from the repo plus this file, without relying on the old chat context.

## Prompt To Generate This Handoff

```text
Create a comprehensive handoff document for this repo/session before I archive or clean up Codex history.

Include:
- repo/path and branch
- current goal
- what we already completed
- files touched or investigated
- commands/tests already run
- known errors, warnings, or failing checks
- open decisions
- constraints, user preferences, and do-not-touch areas
- the next 3-7 concrete steps

Also include a reactivation prompt I can paste into a fresh Codex chat so it can continue from this handoff without relying on the old chat context.

Save the handoff in a sensible repo-local place like docs/codex-handoffs/YYYY-MM-DD-topic.md unless this repo already has a better handoff location.
```

## Reactivation Prompt

```text
We are continuing from this handoff. Read this document first, inspect the current repo state, verify what still applies, and continue from the next steps without assuming the old chat context is available.
```

## Context

- Repo/path:
- Branch:
- Related chat/session:
- Current goal:
- User preferences or constraints:

## What Changed

- 

## Files Touched Or Investigated

- 

## Commands And Checks Already Run

- 

## Known Issues

- 

## Open Decisions

- 

## Next Steps

1. 
2. 
3. 

## Do Not Touch / Be Careful

- 
