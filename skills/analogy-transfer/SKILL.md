---
name: analogy-transfer
description: "Solve a problem by systematically importing solutions from other domains: abstract the problem's deep structure, find 3–5 domains that share that structure, study how each solved it, and translate the mechanisms back — with an explicit disanalogy check. Use for 'how do other fields handle this?' and stuck problems that feel like they must have been solved somewhere before."
compatibility: Created for Zo Computer
metadata:
  author: rob.zo.computer
---

# Analogy Transfer

Use this skill to solve a problem by finding where else its deep structure appears and importing the mechanisms that worked there. Most hard problems have already been solved — in a different domain, under a different name.

## Purpose

Analogy is the engine of invention (immunology → spam filtering, biological evolution → genetic algorithms, just-in-time manufacturing → lean software). But casual analogy fails by matching surface features instead of structure, and by ignoring where the analogy breaks. This skill makes the mapping explicit in both directions: what transfers, and what doesn't.

## Procedure

1. State the problem concretely.
2. **Abstract to structure**: strip domain nouns and restate the problem in structural terms — flows, constraints, incentives, feedback loops, adversaries, scarcity. ("How do we onboard users?" → "How does a system get a newcomer to competence before frustration exceeds motivation?")
3. **Search for structural twins**: find 3–5 domains sharing that structure. Deliberately search far — biology, military, cities, games, religion, logistics, law, sports. Nearby domains give weak analogies.
4. For each twin domain:
   - How does it solve the structural problem?
   - What named mechanism does the work?
5. **Translate back**: for the 2–3 strongest mechanisms, state what the equivalent move would be in the original domain.
6. **Disanalogy check**: for each candidate transfer, name where the domains differ and whether the difference breaks the mechanism. This step is mandatory — it is what separates insight from vibes.
7. Recommend the strongest transfer(s) and the cheapest way to pilot them.

## Output format

Use this concise structure unless the user asks otherwise:

```markdown
## Problem
...

## Structural form
...

## Structural twins
| Domain | Their version of the problem | Their mechanism |
|---|---|---|

## Candidate transfers
1. **Mechanism → translated move**: ...

## Disanalogy check
| Transfer | Where the analogy breaks | Survives? |
|---|---|---|

## Recommendation
...
```

## Guardrails

- Match structure, not vocabulary. Two domains that share buzzwords rarely share mechanisms.
- At least one twin must come from a domain far from the user's field.
- The disanalogy check is not optional; an analogy without a stated breaking point is decoration.
- Prefer mechanisms with a track record over poetic parallels.

## Canonical questions

- "How should we handle content moderation at scale?" (immune systems, courts, city policing)
- "How do we keep our best engineers from leaving?" (sports free agency, academic tenure, guilds)
- "How should our API handle abusive clients?" (traffic engineering, antibody response, bouncer economics)
- "How do we onboard new users faster?" (military basic training, video game tutorials, apprenticeships)
- "How do we price this new product?" (airline yield management, theater tickets, wine)

Poor fits: problems already well-solved in-domain (just use the standard solution), and problems so novel or so simple that structural twins add noise.
