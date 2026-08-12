---
name: dp-solve
description: Use dynamic-programming-style reasoning as a general thinking tool for any problem, decision, strategy, explanation, or analysis. Decompose the question into overlapping subproblems, memoize subanswers, then synthesize a solution from the memo table.
compatibility: Created for Zo Computer
metadata:
  author: rob.zo.computer
---
# DP Solve

Use this skill when the user invokes `dp-solve`, asks for dynamic-programming-style reasoning, or wants a problem solved by decomposing it into reusable subproblems.

This is not about literally writing dynamic programming code unless the user's question is a programming problem. It uses DP as a thinking analogy: define the problem state, identify base cases, decompose into subproblems, reuse repeated subanswers, and synthesize a final answer.

## Invocation

Preferred form:

```text
dp-solve q=<question or problem>
```

Examples:

```text
dp-solve q=Should we build this feature?
dp-solve q=Why does this system feel brittle?
dp-solve q=How should I think about hiring for this role?
dp-solve q=What is the best way to explain Zo Computer?
```

If `q` is missing, ask for the question or problem.

## Purpose

Many hard questions are not single-step questions. They are composed of smaller questions, and those smaller questions often recur across multiple branches of the reasoning. A normal recursive decomposition can duplicate work or produce inconsistent answers. DP-style reasoning turns the problem into a subproblem graph, keeps a memo of subanswers, and reuses them when synthesizing the final answer.

**When to use vs. alternatives:** dp-solve shines when subquestions *recur* across branches. If the question is a linear causal drill-down, use `five-whys`/`n-whys`. If it's a one-shot comparison between options, a decision matrix may suffice. If there's no overlap between subproblems, this is just ordinary decomposition and the memo table adds ceremony.

## Canonical questions

- Should we migrate off this vendor? (cost, risk, and timing subquestions recur across options)
- How should I think about hiring for this role? (team needs, market, budget overlap across candidate profiles)
- What is the best way to explain Zo Computer? (audience, metaphor, and differentiator subquestions recur across framings)
- Why does this system feel brittle? (shared root causes appear under multiple symptoms)

## Procedure

 1. **State the problem.** Rewrite `q` as the target problem to solve.
 2. **Define the objective.** Say what a good answer should optimize for: truth, actionability, simplicity, speed, robustness, user value, explanatory power, etc.
 3. **Define the state.** Identify the core state variables that determine the answer.
 4. **Identify base cases.** List facts, constraints, definitions, or judgments simple enough to accept directly.
 5. **Decompose into subproblems.** Break the target problem into smaller questions.
 6. **Detect overlap.** Notice where different branches depend on the same subquestion.
 7. **Build a memo table.** Assign each subproblem an ID, answer it once, include confidence, and note where it is reused.
 8. **Solve bottom-up.** Use the memoized subanswers to answer larger subproblems.
 9. **Synthesize.** Combine the solved subproblems into the final answer.
10. **Extract reusable lemmas.** Name any subanswers that are likely to be useful in future reasoning.

## Output format

Use this structure unless the user asks otherwise:

```markdown
## Problem
...

## Objective function
A good answer should optimize for: ...

## State variables
- ...

## Base cases
- ...

## Subproblem graph
- P0: Main problem
  - P1: ...
  - P2: ...
  - P3: ...

## Memo table
| ID | Subproblem | Answer | Confidence | Reused by |
|---|---|---|---|---|
| B1 | ... | ... | High/Medium/Low | P1, P3 |
| P1 | ... | ... | High/Medium/Low | P0 |

## Bottom-up synthesis
...

## Final answer
...

## Reusable lemmas
- ...

## Next check
- ...
```

## Guardrails

- Do not overcomplicate simple questions. If the answer is obvious, use a small memo table or say the DP frame is unnecessary.
- Keep subproblems meaningfully smaller than the parent problem.
- Reuse memoized answers instead of restating them differently.
- Track confidence. Do not let a low-confidence base case silently support a high-confidence final answer.
- If two memo entries conflict, surface the conflict and resolve it before synthesis.
- Avoid false precision. The memo table is a reasoning aid, not proof that the answer is mathematically certain.
- For emotional, interpersonal, or organizational topics, include incentives, constraints, feedback loops, and human needs as possible state variables.