---
name: pubmax-code-review
version: 1.0.0
description: Review every PUBMAXX PR against product, browser, mobile, and honesty contracts.
---

# PUBMAXX code review

Apply this checklist to every PUBMAXX PR. Require evidence for claims. Classify
findings as `severe`, `important`, or `nit`.

## Contract checks

- For every authenticated surface, prove the flow in a signed-in browser.
  Commit the screenshot or recording in the branch and link it from the PR
  body. A PR body image must exist in the branch.
- Check the auth bootstrap race. No auth-required action may fire anonymously.
  Use `authedActionFetch` and wait for the session contract before the action.
- Check every user action for visible success and visible failure. No silent
  button, swallowed error, or stuck pending state.
- Check reconnect behaviour. Realtime, polling, and subscriptions must recover,
  refetch, or self-heal after a drop without a reload.
- Check offline copy. It must say what did not happen and preserve any safe
  local work. Never show success for an unconfirmed write.

## Product truth

- Do not invent prices, hours, heritage, availability, people, or activity.
- Name Provenance at the point of the claim. Keep Sourced, Contributor,
  Anecdote, and Community observations distinct.
- Keep thin nights thin. Missing evidence is an honest state, not a prompt to
  fill the surface with guesses.
- Product copy uses British English and contains no em dashes.

## Mobile and interaction

- Use `dvh` or `svh` for viewport-bound layouts and respect safe-area insets.
- Keep form inputs at least 16px to avoid mobile zoom.
- Set `user-select` deliberately on selectable text and controls.
- Use `touch-action: pan-y` where vertical page scrolling must survive gestures.
- Check fixed bars, keyboard space, focus, hit targets, and narrow-screen overflow.

## Review severity

- `severe`: security, privacy, data loss, account ownership, false product
  claims, or a broken primary flow. Block merge.
- `important`: regression, inaccessible action, missing failure state, broken
  mobile behaviour, or a violated architecture or honesty contract. Fix before
  merge unless the owner records an explicit decision.
- `nit`: clarity, naming, or low-risk polish with no contract impact. Fix when
  useful; do not hide a higher-severity finding among nits.

## Evidence gate

Validate suggested fixes in the real branch. Run the narrow test, lint, typecheck,
or build command that proves the claim. Do not accept a suggested fix until it
actually builds and the relevant behaviour is rechecked.
