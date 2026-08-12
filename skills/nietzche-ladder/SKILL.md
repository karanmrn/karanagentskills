---
name: nietzche-ladder
description: Explain any topic at three escalating Nietzschean levels — Camel, Lion, Child — where each level responds directly to the one before it, moving from burden-bearing understanding, to critical negation and freedom, to creative affirmation. Use when the user asks for a "nietzche ladder", "Nietzsche ladder", "camel/lion/child explanation", or any three-stage breakdown in the spirit of Nietzsche's metamorphoses.
compatibility: Created for Zo Computer
metadata:
  author: rob.zo.computer
---

# Nietzche Ladder

Produce a three-rung cascading explanation of the user's topic using Nietzsche's three metamorphoses of the spirit: **Camel**, **Lion**, and **Child**. Each rung is a different posture toward understanding. Crucially, **each level responds to the one before it** — engaging directly with what the previous level said, conceding what was right, and pushing past what was incomplete.

The skill name intentionally uses the user's spelling, `nietzche-ladder`; in the prose, use **Nietzsche**.

## Output format

Render exactly three sections, in this order, using these headings verbatim:

1. `## 1. Camel`
2. `## 2. Lion (responding to Camel)`
3. `## 3. Child (responding to Lion)`

Open with a single H1 title: `# <Topic> — A Nietzsche Ladder` (or a close variant if the topic phrasing warrants it).

## Voice of each rung

**1. Camel.** The Camel carries inherited weight: facts, duties, history, traditions, constraints, authorities, and the serious claims others have made about the topic. It is patient, disciplined, and honest. It explains the conventional burden of the topic without mockery: what one must know, what has been handed down, what is difficult, and why the difficulty matters. Plain but weighty prose. 1–2 paragraphs.

**2. Lion (responding to Camel).** Opens by engaging the Camel — "You have carried the burden well, but…" or "Yes, those are the old tablets; now ask who wrote them." The Lion says **No**: it challenges inherited assumptions, exposes hidden values, names resentments or evasions, and refuses false necessity. It does not merely rebel for style; it wins a clearing where freedom becomes possible. Sharper, more critical, more aphoristic. 1–2 paragraphs.

**3. Child (responding to Lion).** Opens by engaging the Lion — "Your No was necessary, but it is not yet creation." The Child says **Yes**: it turns critique into fresh creation, play, innocence, experimentation, and a new beginning. It should be wiser than both Camel and Lion, not cuter or more naive. It does not return to the old burden, and it does not remain trapped in negation. It shows what the topic becomes when approached with creative affirmation. Clear, vivid, quietly joyful prose. 2–4 paragraphs, the longest section.

## Cascading rule

Each level after the first **must** begin by engaging the previous level — agreeing with part of it, then pushing past it. The transitions are the soul of this skill. Examples of good openings:

- "You have carried the burden well, but…"
- "Yes, those are the old tablets; now ask who wrote them."
- "Your No was necessary, but it is not yet creation."
- "Good: you broke the idol. Now what can dance in the cleared space?"

Never have a level ignore the previous one.

## Topic handling

- If the user gives only a topic, use it as-is.
- If the topic is a process or event, the Camel should carry the inherited account, the Lion should challenge its assumed necessity or moral framing, and the Child should imagine what new possibility the event reveals.
- If the topic is a thing or concept, the Camel should explain what it is and why it matters, the Lion should ask what values or fears are hiding inside that explanation, and the Child should re-create the concept as a living possibility.
- If the topic is contested or sensitive, keep each rung honest about uncertainty. The Lion may be fierce, but it must not become careless.

## Style constraints

- Do not write a generic three-part explanation with Nietzschean labels pasted on top. The metamorphosis must shape the thinking.
- Do not make the Child simplistic. The Child is the deepest rung: creative, affirmative, playful, and free.
- Do not let the Lion become mere contrarianism. It negates in order to clear space for creation.
- Do not let the Camel become dull summary. It should dignify the inherited burden.
- Avoid excessive Nietzsche name-dropping. Zarathustra, will to power, eternal recurrence, master/slave morality, and other Nietzschean terms may appear only when they genuinely clarify the topic.
- Use direct, memorable prose. Aphorism is welcome; obscurity is not.

## Length target

Roughly 500–900 words total. Child is the longest, Camel is the most grounded, Lion is the sharpest. Each level should feel like a real metamorphosis — not just a change in tone.

## Anti-patterns to avoid

- Treating Camel as "beginner," Lion as "intermediate," and Child as "advanced." They are existential postures, not school levels.
- Making the Lion the final answer. Negation is a bridge, not a home.
- Making the Child sentimental, cute, or vague.
- Repeating the same point in different words across rungs.
- Letting any rung stand alone without engaging the previous one.

## Canonical topics

Best for topics where inherited convention weighs heavily and creative reframing is possible:

- Marriage
- The 40-hour work week
- Academic peer review
- Homeownership
- Retirement

Poor fits: neutral technical mechanisms ("how does TCP work") where there's no inherited burden to carry or negate.

## Invocation

When the user invokes this skill, ask only for the topic if one isn't given. Otherwise, produce the ladder directly with no preamble.
