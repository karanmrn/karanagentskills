---
name: ladder-of-abstraction
description: Use the ladder of abstraction as a thinking tool for any question, explanation, writing task, strategy, or concept where the user needs to move between concrete examples and abstract principles.
compatibility: Created for Zo Computer
metadata:
  author: rob.zo.computer
---

# Ladder of Abstraction

Use this skill when a question or idea would benefit from moving deliberately between concrete particulars and abstract generalizations.

## Purpose

The ladder of abstraction clarifies thinking by placing an idea at different levels: specific observations at the bottom, categories and patterns in the middle, and broad principles or values at the top. Good thinking can move up and down the ladder without getting stuck in vague abstraction or isolated details.

## Procedure

1. Identify the current level of abstraction in the user's question.
2. Move down the ladder: give concrete examples, instances, sensory details, mechanisms, or cases.
3. Move up the ladder: name the broader category, pattern, principle, value, or theory.
4. Check whether the abstraction still fits the concrete examples.
5. Use the right level for the task:
   - Concrete for action, debugging, evidence, and communication.
   - Middle for pattern recognition and planning.
   - Abstract for principles, strategy, and meaning.
6. If helpful, rewrite the answer at multiple levels.

## Output format

Use this concise structure unless the user asks otherwise:

```markdown
## Current level
...

## Down the ladder: concrete instances
- ...
- ...

## Middle level: pattern or category
...

## Up the ladder: principle or meaning
...

## Best level for this task
...
```

## Guardrails

- Avoid vague abstractions that cannot be tied back to concrete examples.
- Avoid drowning in details without naming the pattern.
- When explaining, move down to examples before moving back up to the principle.
- When deciding, choose the abstraction level that changes the action.

## Canonical questions

- "My pitch isn't landing — is it too abstract or too concrete?"
- "We keep arguing about this feature; are we even talking about the same level of the problem?"
- "Turn this pile of user complaints into a product principle."
- "This mission statement feels empty — ground it."
- "Why does this essay feel simultaneously vague and rambling?"

Poor fits: questions that live entirely at one level (a pure implementation bug, a pure values debate with no instances available).