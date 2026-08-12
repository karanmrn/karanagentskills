# ideate (standing rule, ALL projects)
When Karan proposes any new idea, feature, or product direction, invoke the `ideate` skill (`~/.claude/skills/ideate/SKILL.md`) BEFORE executing anything: grill one question at a time, run a top-tier agent panel on the idea, then the gated implement/verify/review/close pipeline. Never just build the idea as stated.

# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

# Engineering standards (merged from kunchenguid/dotfiles, 2026-07-25)

## Writing
- Before each task, find and read all `CONTEXT.md` files in the repository. Use the ubiquitous language that these files define.
- Never use the em dash. Use a plain dash instead.
- Never add your agent name as a commit co-author.
- Never manually modify CHANGELOG.md or any file marked auto-generated.

## UI descriptions

- Do not add subtitles, helper text, or descriptive copy below headings, labels,
  cards, or settings by default.
- Use one concise, self-explanatory heading or label.
- Add supporting copy only when the user requests it or when it prevents
  misunderstanding or error.
- Never use supporting copy to repeat the heading or label.

## ASD-STE100 Simplified Technical English (standing rule, ALL projects)
Write all technical text in ASD-STE100 Simplified Technical English. It is a
controlled writing standard from the aerospace and defence industries. Its
purpose is text that a reader understands correctly on the first read.

Rules:
- Use approved words only. Give each word one meaning.
- Use one word for one idea. Do not use two words for the same thing.
- Write short sentences. Use 20 words or less in an instruction.
- Use the active voice. Write "Turn the switch", not "The switch must be turned".
- Write short paragraphs. Keep one topic in each paragraph.

This applies to documentation, briefs, PR bodies, commit messages, error text,
UI copy, and chat replies. Keep exact technical terms, code, API names, CLI
commands, and error strings unchanged.

## Technical judgment
- When making technical decisions, do not give much weight to development cost.
  Prefer quality, simplicity, robustness, scalability, and long-term maintainability.
- For one-off or infrequent operational work, start with the simplest direct end-to-end path.
  Do not build wrappers, control planes, policy layers, custom verifiers, or automation
  unless the direct path exposes a concrete blocker or repeated need that justifies it.

## Bug fixing
- Always start by reproducing the bug end-to-end, as closely to how a real user would
  hit it as possible. This confirms you found the real cause, so the fix actually works.

## Quality bar
- When end-to-end testing a product, be picky about the UI and obsessed with pixel
  perfection. If something clearly looks off, get it fixed even when unrelated to the
  current task.
- Apply the same standard to lint errors, test failures, and test flakiness. If you see
  one, get it fixed even when it is not caused by current work.

## Swarm safety
- Before using dynamic workflows, ultra code, or any harness feature that immediately
  spawns a large swarm of subagents, explain the tradeoffs and ask for explicit approval.
