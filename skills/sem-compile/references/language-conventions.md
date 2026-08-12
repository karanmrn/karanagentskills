# Sem language conventions

## Contents

- [The premise](#the-premise)
- [The repository is the standard library](#the-repository-is-the-standard-library)
- [Familiar affordances](#familiar-affordances)
- [Flow and application boundaries](#flow-and-application-boundaries)
- [Bindings, configuration, visibility, and returns](#bindings-configuration-visibility-and-returns)
- [Local operators](#local-operators)
- [Invented constructs](#invented-constructs)
- [Type-like hints and comments](#type-like-hints-and-comments)
- [Independent-handoff check](#independent-handoff-check)

## The premise

Sem is interpreted prose for composing semantic functions. A program is meant
to be read and applied by a capable language model. It does not parse,
type-check, or need to be valid Haskell. Punctuation, indentation, names, type
hints, and operators are aids to shared understanding, not syntax rules.

A good program makes six things recoverable without the original conversation:

1. the source values;
2. every semantic function application;
3. the input and local configuration of each application;
4. dependencies and independent branches;
5. iteration bounds or semantic stopping tests;
6. the visible results and their presentation order.

Use the least ceremony that makes those facts clear. A three-line pipeline can
be complete; an unfamiliar construct can be safer than a familiar symbol whose
meaning is left ambiguous.

## The repository is the standard library

Every semantic skill under this repository's `skills/` directory is potentially
available as a standard-library function through its full `SKILL.md` contract.
The folder slug is the stable identity:

```text
skills/question-forge/SKILL.md         -> question-forge
skills/assumption-audit/SKILL.md       -> assumption-audit
skills/first-principles-thinking/...   -> first-principles-thinking
```

Programs may camel-case slugs for readability:

```text
questionForge          -> question-forge
assumptionAudit        -> assumption-audit
firstPrinciplesThinking -> first-principles-thinking
```

Hyphenated spelling is equally valid. An optional `use [...]` line can make
resolution obvious, but it is not an import system.

Do not select a function from its name alone. Read the relevant `SKILL.md` and
honor its input conditions, ordered procedure, output form, stopping rule, and
guardrails. If its real contract is only adjacent to the needed move, define a
local operator instead. `sem-compile` and `sem-run` are language tooling rather
than ordinary semantic functions; omit them from programs unless the requested
program is explicitly about compilation or execution.

## Familiar affordances

These forms carry their usual programming intuitions. They are examples, not a
closed grammar.

| Form | Ordinary reading |
| --- | --- |
| `x >>> f >>> g` | Apply `f` to `x`, then apply `g` to the result. |
| `x >>> (f &&& g)` | Apply `f` and `g` independently to the same `x`. |
| `f <|> g` | Choose, race, or fall back between routes as locally explained. |
| ``f `with` { tone = dry }`` | Configure this application of `f`. |
| `map f xs` | Apply `f` independently to each item of `xs`. |
| `repeat 3 f` | Apply `f` three times, passing the current value forward. |
| `repeat f until stable` | Iterate with a stated semantic stopping test. |
| `let x = ...` or `x <- ...` | Name a value or application result. |
| `pure [x, y]` | Declare returned artifacts. |
| `hide x` / `reveal x` | Control final visibility without erasing the trace. |
| `order [x, y, z]` | Declare presentation order, not execution order. |

Equivalent prose, do-notation, records, arrows, tables, diagrams, or invented
combinators are welcome. None of these spellings is privileged.

## Flow and application boundaries

An **application** is a semantic transformation or judgment performed by a
function. Standard-library functions and local functions both count. A
selector, predicate, critic, synthesizer, or stopping test also counts when it
must interpret meaning rather than merely rearrange files.

The following are normally structural, not applications:

- naming a value;
- constructing or projecting a literal record;
- linking an existing artifact;
- noting that dependencies are ready;
- hiding, revealing, or ordering already-produced results.

If one of those moves requires judgment, name the judgment as an application.
For example, `order [story, song]` is structural, while “choose the more honest
story” is a semantic selector and must be explicit.

Do not manufacture judgment merely to regularize shapes. When the selected
contract's documented procedure includes the needed interpretation, its worker
can receive the declared semantic text directly—for example, an enclosing
result containing the claim it audits, or the exact prior value the user
declared as the next round's input. This does not relax exact-contract
selection: if identifying the target or converting the input is a distinct
material judgment outside that procedure, expose it as an application. Naming
failure status in the final report is bookkeeping, not a separate semantic
application.

### Sequence

`a >>> f >>> g` means the result of `f a` is the declared input to `g`. When `g`
also needs an earlier value, show it:

```haskell
audit <- assumptionAudit plan
guards <- inversion { goal = plan.goal, evidence = audit }
```

Do not rely on a worker remembering an upstream value that is absent from its
declared input.

### Fan-out and synthesis

`x >>> (f &&& g &&& h)` creates independent applications with the same declared
input. It returns a collection of branch results; it does not silently merge
them.

When the branches must be reconciled, make the synthesis another application:

```haskell
views <- question >>> (firstPrinciplesThinking &&& inversion)
answer <- views >>> synthesize
```

Define `synthesize` locally unless a repository skill's actual contract matches
the desired reconciliation.

### Choice and fallback

`f <|> g` is intentionally overloaded. Add a local explanation whenever the
route affects meaning:

```haskell
chooseByShape (decisionMatrix <|> firstPrinciplesThinking)
  -- choose the matrix only for 2-6 concrete named options;
  -- otherwise choose first principles; never run both
```

The semantic route decision is itself an application. A purely mechanical
fallback such as “use the second file if the first is missing” may remain
structural, but say so. Never let `<|>` conceal whether branches both run,
whether one judges the other, or whether failure triggers the alternative.

### Mapping

`map f items` creates one application of `f` per item, each using only that item
and the application-local configuration. State how collection order is
preserved and what happens to an item that cannot be processed when it matters.

### Iteration and stopping

Every open-ended iteration needs a bound or a stopping test. A semantic stopping
test is a separate application on the previous and current values.

```haskell
repeat up to 4 rounds:
  next <- sharpen current
  done <- stableEnough { previous = current, current = next }
  stop when done says the central distinction and stakes are unchanged
```

Explain what survives between rounds and what is returned on exhaustion. Avoid
`until good`, `until done`, or `until stable` without defining what those words
mean for this program.

## Bindings, configuration, visibility, and returns

Bindings give later applications stable inputs. Prefer names that describe the
semantic value (`forgedQuestion`, `failureModes`) rather than its container
(`output2`).

Configuration after `with` belongs only to that application. It refines the
skill contract but does not replace it. For example, asking `lyric` for a folk
ballad still retains lyric's recurrence, image, compression, and no-borrowed-
voice guardrails.

Visibility is separate from dependency. `hide audit` means “do not foreground
this intermediate in the returned presentation,” not “delete it” or “deny it to
a declared downstream application.” Declare visible artifacts explicitly, and
use `order [...]` when sequence matters to the reader.

## Local operators

Define a local operator when no repository skill truly performs the move. A
local definition should give an independent application worker enough context
to act without the original conversation:

```haskell
local extractTension(input: DilemmaAndForgedQuestion) -> CreativeBrief:
  purpose: preserve the conflict that downstream forms should embody
  moves:
    - identify one primary opposed pair supported by the input
    - retain at most two secondary pairs
    - keep both sides as live goods; do not recommend a choice
  return:
    a standalone brief containing the situation, forged question,
    primary tension, and supporting tensions
  stop:
    after one supported primary pair is clear
  guardrails:
    do not invent biographical facts or collapse a side into a straw man
```

The labels are optional. The substance is not: state purpose, accepted input,
ordered or otherwise defining moves, output shape, stopping condition, and
characteristic guardrails. For a trivial one-pass transformation, “stop after
one result” is enough.

Local operators belong to the program. They do not become standard-library
skills merely because they were useful once.

## Invented constructs

Invent a construct when it conveys the program better than stretching existing
notation. Give it a short local gloss that answers:

- what values enter and leave;
- which semantic applications it creates;
- which can proceed independently;
- how it terminates;
- how failures or empty results affect the surrounding flow.

For example:

```haskell
tension
  >>> refract [security, freedom, identity]
      -- create one independent `interrogateFrame` application per named frame;
      -- return all non-empty readings in frame order
  >>> keep productiveDisagreement
      -- one local semantic selector; retain at most three readings that
      -- disagree without relying on incompatible facts
```

`refract` and `keep` need not be global language features. The gloss makes this
single use executable.

## Type-like hints and comments

Use annotations such as `Program [Artifact]`, records, algebraic-looking values,
or signatures when they communicate shape. They make no promise of machine
validity:

```haskell
question :: ForgedQuestion
choice = Stay <|> Leave  -- unresolved value alternatives, not route selection
```

Comments may carry essential semantics. A construct plus its comment is one
piece of executable prose; removing the comment can change the program.

## Independent-handoff check

Before treating a program as complete, imagine handing each application to a
fresh reader. For every application, verify that the reader can identify:

- the exact operator contract or complete local definition;
- the declared input artifacts, not the whole conversation;
- application-local options;
- the standalone result it must return;
- the stop condition and relevant guardrails.

Then imagine handing the whole program to another fresh reader. They should be
able to enumerate applications, dependencies, parallel groups, dynamic
expansion, visible returns, and final order while being free to ignore harmless
surface irregularities.
