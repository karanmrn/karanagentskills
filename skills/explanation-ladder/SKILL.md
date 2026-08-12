---
name: explanation-ladder
description: Explain any topic at five escalating levels — High School, College, PhD, Philosopher, Gigabrain — where each level responds directly to the one before it, correcting, deepening, or reframing it. Use when the user asks for an "explanation ladder", a "five-level explanation", "ELI5 to galaxy brain", or any cascading multi-level breakdown of a topic.
compatibility: Created for Zo Computer
metadata:
  author: rob.zo.computer
---

# Explanation Ladder

Produce a five-rung cascading explanation of the user's topic. Each rung is a person at a different depth of understanding. Crucially, **each level responds to the one before it** — engaging directly with what the previous level said, conceding what was right, and pushing past what was incomplete.

## Output format

Render exactly five sections, in this order, using these headings verbatim:

1. `## 1. High School`
2. `## 2. College (responding to High School)`
3. `## 3. PhD (responding to College)`
4. `## 4. Philosopher (responding to PhD)`
5. `## 5. Gigabrain (responding to Philosopher)`

Open with a single H1 title: `# <Topic> — A Cascading Explanation` (or a close variant if the topic phrasing warrants it).

## Voice of each rung

**1. High School.** Plain language. Concrete people, places, dates, numbers. No jargon. Tells the story the way a curious teenager would tell it to a friend. 4–7 sentences.

**2. College (responding to High School).** Opens by engaging the previous level — "That's the right shape, but…" or "You've named the surface; underneath…". Introduces the named mechanisms, the standard textbook framing, the first technical vocabulary. Corrects oversimplifications without sneering. ~1 paragraph.

**3. PhD (responding to College).** Engages the College framing and shows where the literature complicates it. Cites named thinkers, models, papers, debates. Brings precise technical language. Identifies the deepest causal mechanism the previous level only gestured at. ~1 paragraph, denser.

**4. Philosopher (responding to PhD).** Steps outside the technical frame. Concedes the machinery is correct but reframes what it *means*. Asks what the categories presuppose. Connects the topic to deeper questions about knowledge, trust, power, meaning, time, or the human condition. Beautiful prose, no equations. ~1–2 paragraphs.

**5. Gigabrain (responding to Philosopher).** This is the hardest rung to get right. The Gigabrain is **wiser, not jargonier**. They speak in clear, almost plain language, but they see one level deeper than the philosopher — they name the thing underneath the thing the philosopher named. They are a great communicator. No buzzwords, no equations, no name-dropping. The voice is calm, slightly oracular, deeply observed. They often end on a single resonant sentence that recasts the whole topic. ~3–5 paragraphs, the longest section.

## Hard rules for the Gigabrain rung

- **No jargon.** Banned vocabulary unless quoting: "Bayesian," "eigenvalues," "Jacobian," "topology," "phase transition," "metastable," "saddle point," "stochastic," "regime," "manifold," "discrete-time map," "entropy sink," "synchronization device."
- **No equations, no Greek letters, no acronyms invented for the occasion.**
- **No name-dropping** of academics or schools of thought (the Philosopher rung handles that).
- Use ordinary words to do extraordinary work. If you reach for a fancy term, replace it with the plainest accurate phrase.
- The Gigabrain should feel like a wise elder who has spent a lifetime watching this kind of thing happen and has finally found the simplest way to say it.

## Cascading rule

Each level after the first **must** begin by engaging the previous level — agreeing with part of it, then pushing past it. The transitions are the soul of this skill. Examples of good openings:

- "That's the right shape, but…"
- "You've named the mechanisms but understated their interaction."
- "Your models are elegant, but they describe the machinery while missing the metaphysics."
- "Beautifully said, but I'd push one step further."

Never have a level ignore the previous one.

## Topic handling

- If the user gives only a topic, use it as-is.
- If the topic is a process or event ("the fall of Rome", "the 2008 crisis", "consciousness", "language acquisition"), the ladder works naturally.
- If the topic is a thing or concept ("entropy", "love", "money"), frame each rung as an explanation of *what it is and why it matters*.
- If the topic is contested or sensitive, keep each rung honest about uncertainty rather than confident-sounding for the sake of the form.

## Length target

Roughly 700–1200 words total. Gigabrain is the longest, High School the shortest. Each level should feel meaningfully deeper than the last — not just longer.

## Anti-patterns to avoid

- Making the Gigabrain rung *harder* than the PhD rung. It should be *deeper but simpler*.
- Letting any rung stand alone without engaging the previous one.
- Padding with throat-clearing ("It's important to note that…").
- Repeating the same point in different words across rungs. Each rung must add a genuinely new layer.
- Using the same hedge or metaphor in two different rungs.

## Canonical topics

Topics with real depth at every rung work best — a mechanism, a literature, a philosophical dimension, and a human truth underneath:

- Why is the sky blue?
- Inflation
- How does evolution produce altruism?
- What is money?
- Sleep

Poor fits: trivia with no depth ("what year did X happen"), pure how-to questions, topics where the PhD and Gigabrain rungs would say the same thing.

## Invocation

When the user invokes this skill, ask only for the topic if one isn't given. Otherwise, produce the ladder directly with no preamble.
