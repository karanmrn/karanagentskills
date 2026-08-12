---
name: counterfactual
description: Reason rigorously about "what if X had been different" — isolate the minimal change, propagate consequences forward step by step, and separate what almost certainly follows from speculation. Use for historical what-ifs, post-mortems, decision regret, and attributing causes ("did X actually matter?").
compatibility: Created for Zo Computer
metadata:
  author: rob.zo.computer
---

# Counterfactual

Use this skill to reason about alternate histories with discipline: change one thing, hold everything else fixed, and propagate consequences forward honestly — including the forces that would have pushed events back toward the same outcome.

## Purpose

Counterfactuals are how causes are actually tested — "did X matter?" means "would the outcome differ without X?" But casual counterfactual talk cheats: it changes many variables at once, propagates only the convenient consequences, and ignores equilibrium pressures that make many outcomes overdetermined. This skill imposes the discipline.

## Procedure

1. State the actual history and the outcome of interest.
2. Define the **minimal intervention**: the single, precise change to consider. Reject vague interventions ("if things had gone better") — demand one lever at one moment.
3. Check plausibility: was the intervention genuinely possible at the time, or does it smuggle in hindsight?
4. Propagate forward in explicit steps:
   - **First-order**: what immediately changes?
   - **Second-order**: how do other actors and systems respond?
   - **Equilibrium check**: what forces push back toward the original outcome? Was the outcome overdetermined (many paths led there) or contingent (this path was necessary)?
5. Grade each propagation step: **near-certain / probable / speculative**. Stop propagating when everything downstream is speculative.
6. Conclude: how much did X actually matter? Assign the outcome to *contingent on X* or *overdetermined regardless of X*.

## Output format

Use this concise structure unless the user asks otherwise:

```markdown
## Actual history
...

## Minimal intervention
...

## Propagation
| Step | Consequence | Confidence |
|---|---|---|
| 1st order | ... | Near-certain |
| 2nd order | ... | Probable |
| 3rd order | ... | Speculative |

## Equilibrium pressures
...

## Verdict: contingent or overdetermined?
...
```

## Guardrails

- One intervention at a time. If the user's question bundles several, split them.
- Always run the equilibrium check — most naive counterfactuals fail by ignoring restoring forces.
- Label speculation as speculation; the honesty of the confidence grades is the whole value.
- Do not use the counterfactual to relitigate blame; use it to measure causal weight.

## Canonical questions

- "Would the 2008 crisis have happened without Lehman failing?"
- "If we had launched 6 months earlier, would we have won the market?"
- "Did hiring that VP actually cause the turnaround, or was it already underway?"
- "What if I had taken the other job offer?"
- "Would the project have shipped on time if we hadn't switched frameworks?"

Poor fits: future hypotheticals (that's scenario planning, not counterfactual reasoning), and questions where no outcome of interest is specified.
