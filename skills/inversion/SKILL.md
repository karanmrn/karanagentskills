---
name: inversion
description: Solve a problem backwards by asking how to guarantee failure, then negating. Use for goals, plans, designs, habits, or strategies where the failure modes are easier to enumerate than the success path — "how do I succeed at X" becomes "how would I guarantee X fails, and how do I avoid that."
compatibility: Created for Zo Computer
metadata:
  author: rob.zo.computer
---

# Inversion

Use this skill when a goal is fuzzy but its failure modes are vivid. Instead of asking "how do I achieve X?", ask "how would I guarantee X fails?" — then systematically negate each failure path. Avoiding stupidity is often more tractable than seeking brilliance.

## Purpose

Forward reasoning toward a goal suffers from an unbounded search space: there are infinite ways to try to succeed. Failure is usually more enumerable — a handful of well-known ways things die. Inversion converts an open-ended optimization into a bounded checklist of things to not do, which is often more actionable and more honest.

## Procedure

1. State the goal plainly: what does success look like?
2. Invert it: "What would guarantee this fails?" or "If I wanted this to go badly, what would I do?"
3. Enumerate failure modes generously — aim for 5–10. Include:
   - the obvious operational failures
   - the slow, silent failures (neglect, drift, boredom)
   - the self-inflicted failures (ego, overreach, impatience)
   - the environmental failures (market, timing, dependencies)
4. Rank failure modes by likelihood × damage.
5. Negate the top ones: for each, name the concrete guard, habit, or design choice that prevents it.
6. Synthesize: the anti-failure plan, stated positively.

## Output format

Use this concise structure unless the user asks otherwise:

```markdown
## Goal
...

## Inverted question
How would I guarantee this fails?

## Failure modes
| # | Failure mode | Likelihood | Damage |
|---|---|---|---|
| 1 | ... | High/Med/Low | High/Med/Low |

## Guards (negating the top failure modes)
- ...

## The plan, stated forward
...
```

## Guardrails

- Do not stop at the inverted list — always negate back into affirmative guidance.
- Include at least one *self-inflicted* failure mode; plans that only blame the environment are dishonest.
- Distinguish preventable failures from irreducible risks; do not promise guards against the latter.
- If the goal itself is the problem (success would be bad), say so.

## Canonical questions

- "How do I make sure this product launch goes well?"
- "I want this marriage/friendship/partnership to last."
- "How should I structure my portfolio for retirement?"
- "How do we not screw up this migration?"
- "What should I avoid in my first 90 days at this job?"

Poor fits: pure discovery questions ("what should I build?") where failure modes aren't yet defined, and questions needing a single creative leap rather than risk avoidance.
