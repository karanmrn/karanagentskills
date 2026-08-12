---
name: spec-writing
version: 1.0.0
description: Write focused PUBMAXX PRODUCT.md and TECH.md specs when ambiguity or complexity warrants them.
---

# PUBMAXX feature specs

Write specs only when the feature crosses one of these bars:

- **Ambiguity:** multiple materially different implementations exist and a
  human should choose one.
- **Complexity:** the change is more than a few hundred lines.

Small fixes do not get specs. When the bar is met, check in both files under
`specs/<feature>/` with the PR that implements the feature.

## PRODUCT.md

Describe what a Pubmaxxer can see and do. Keep product decisions separate from
implementation details.

Include:

- user problem and intended outcome
- entry points and primary flow
- visible states: loading, empty, offline, error, permission, and success
- exact or representative copy, using British English and no em dashes
- privacy, identity, consent, and provenance rules
- mobile and accessibility expectations
- explicit non-goals and unresolved choices for human review

Every state must tell the truth. Do not promise data, presence, delivery, or
availability that the system cannot confirm.

## TECH.md

Describe how the product contract is implemented without turning the spec into
an unbounded design document.

Include:

- owning routes, components, libraries, stores, and data boundaries
- source of truth for identity, permissions, and persisted state
- request and response shapes at system boundaries
- failure, retry, reconnect, and offline behaviour
- migration, rollout, and compatibility needs
- test plan mapped to the product states and key invariants
- explicit non-goals and decisions still requiring a human

Name one owner for each policy. Prefer existing seams. Do not create a second
projection, pipeline, identity authority, or copy source without recording why.

## Quality gate

Before opening the PR, check that PRODUCT.md and TECH.md agree on names,
states, permissions, and boundaries. Remove speculative detail. If the feature
no longer meets the ambiguity-or-complexity bar, delete the unused spec folder
and keep the decision in the issue or PR instead.
