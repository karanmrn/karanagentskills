# Sem run artifact contract

## Contents

- [Default layout](#default-layout)
- [Top-level artifacts](#top-level-artifacts)
- [Application directories](#application-directories)
- [Result semantics](#result-semantics)
- [Status and run log](#status-and-run-log)
- [Dynamic applications](#dynamic-applications)
- [Retries and resume](#retries-and-resume)
- [Final result and link completeness](#final-result-and-link-completeness)
- [File-scope rules](#file-scope-rules)

## Default layout

Use Markdown for the whole trace and YAML only for the installed skill's UI
metadata. A representative run is:

```text
sem-runs/
  leaving-my-job/
    2026-07-18-1842/
      request.md
      compiler-prompt.md
      program.md
      compile-notes.md
      interpretation.md
      run.md
      inputs/
        source-note.md
      applications/
        001-understand/
          prompt.md
          result.md
          status.md
        002-question-forge/
          prompt.md
          result.md
          status.md
        003-extract-tension/
          prompt.md
          result.md
          status.md
        004-parable/
          prompt.md
          result.md
          status.md
        005-lyric/
          prompt.md
          result.md
          status.md
        006-joke/
          prompt.md
          result.md
          status.md
      finalizer-prompt.md
      final.md
```

Directories and filenames are conventions interpreted by the runner, not a
schema consumed by code. Keep them stable within one run so a fresh agent can
resume from files alone.

## Top-level artifacts

### `request.md`

Preserve the exact immediate request, invocation mode, creation time, and links
to authorized run-local input copies. Do not mix compiler conclusions into the
source record.

### `compiler-prompt.md`

Record the exact no-history handoff used to invoke `sem-compile`. Omit it when
an existing ready program is imported without compilation; explain that in the
run log.

### `program.md`

Contain the squishy executable program and all local definitions or construct
glosses required to interpret it. It is language, not parser input.

### `compile-notes.md`

Record compiler status, standard-library resolution, local operators, style
lowering, inferences, ambiguity, and handoff audit. Imported programs receive
brief import notes if no existing notes accompany them.

### `interpretation.md`

Record the root runner's pre-execution application inventory, declared inputs,
dependencies, parallel groups, dynamic rules, stops, visibility, returns, and
interpretive decisions. Append or add dated amendments for runtime discoveries;
do not rewrite the initial reading as though it had predicted everything.

### `run.md`

Contain the overall status, application table, and append-only narrative log.
It is the human-readable state of the run, not a machine manifest.

### `inputs/`

Contain only authorized copied text/Markdown sources with safe names. Link each
copy from `request.md`. Applications read copies rather than mutable originals.

### `finalizer-prompt.md` and `final.md`

Record the finalizer's exact whole-run prompt and its final artifact. The final
file preserves returned results, links the whole Markdown trace, summarizes
actual execution, and identifies partial or blocked work.

## Application directories

Assign a zero-padded ordinal and readable lowercase name before launching an
application. Ordinals express trace creation order, not necessarily execution
order. Assign all members of a concurrent batch before spawning them.

Each application directory contains:

- `prompt.md`: exact no-history worker prompt and declared read list;
- `result.md`: only for a Succeeded application, the first accepted standalone
  semantic result, immutable after success;
- `status.md`: current status plus append-only attempt notes.

A worker writes only its assigned result. The root writes status and scheduling
metadata. If the host makes direct worker file writes impractical, the worker
may return the artifact body to the root, but the root must copy it without
semantic editing and record the deviation.

Use relative links between artifacts. Do not rely on chat messages as the only
record of an input, result, failure, or scheduling choice.

## Result semantics

Every accepted `result.md` is independently intelligible:

```markdown
# 003 · extractTension

- Function: local `extractTension`
- Inputs: [Forged question](../002-question-forge/result.md)
- Configuration: one primary tension; at most two supporting tensions

## Result

<semantic output>
```

The `## Result` section is the value passed downstream. Provenance above it is
for inspection and must not become accidental semantic input. A downstream
worker receives the declared Result section and its link, not the whole run.

Do not put chain-of-thought or private reasoning into result files. Outputs may
include the reasoning form required by a standard-library skill—such as an
assumption table or why-chain—but not hidden internal deliberation.

Hidden results still receive full directories and remain linked in the final
artifact index. Visibility controls presentation, not trace retention.

## Status and run log

Use these application states in `status.md` and `run.md`:

- **Pending:** known but missing an accepted dependency;
- **Ready:** all declared source inputs are available and all upstream result
  dependencies are accepted;
- **Running:** assigned to a fresh worker;
- **Succeeded:** `result.md` was accepted and is immutable;
- **Failed:** the application reached a terminal failure;
- **Blocked:** a dependency failed or material ambiguity prevents launch.

Use overall run states: Compiling, Needs clarification, Interpreting, Running,
Succeeded, Partial, Blocked, or Failed.

Each status file names the function, declared inputs, worker identity when the
host exposes it, start/end times when practical, attempts, result link, and
failure or retry reason. The run log records scheduling batches, dynamic
expansion, interpretive changes, failures, resume events, and finalization.

Plain language is sufficient. Consistency and recoverability matter more than
one mandated table shape.

## Dynamic applications

Assign dynamic application IDs when their inputs become concrete:

- maps follow source item order;
- repeat bodies and predicates follow round order;
- selected branches follow the selector result;
- invented constructs follow the expansion order recorded in the program.

Record the parent construct and generated IDs in `interpretation.md` or
`run.md`. Each generated semantic call receives the same prompt/result/status
contract as a static application. Do not hide several calls inside one worker
merely because the source used one combinator.

If concurrent completion order differs from ordinal order, preserve the
assigned ordinals. Presentation order still comes from the program's return
declaration.

## Retries and resume

Reserve root `result.md` for the first accepted output and never overwrite it.
Keep failed or malformed attempt material under:

```text
applications/003-name/attempts/
  001-failure.md
  002-prompt.md
  002-failure.md
```

The initial exact prompt remains `prompt.md`; later retry prompts are numbered.
`status.md` links every attempt and the accepted root result when one succeeds.
If an initial or retry worker writes malformed material to `result.md`, move it
unchanged to the next numbered failure file before continuing; never leave a
rejected candidate at the canonical accepted-result path. Retry at most once
automatically and only for a mechanical failure.

Resume reads Markdown state and existing directories. It preserves Succeeded
results, continues unfinished applications, and appends attempts/log entries.
Never overwrite history to make a resumed run appear uninterrupted.

## Final result and link completeness

`final.md` uses this conceptual order:

1. title, overall status, and links to program/interpretation/run log;
2. returned artifacts in declared presentation order, each linked and included
   inline when useful;
3. `## What happened` describing actual value flow and applications;
4. failures/blocked work, or `None`;
5. `## Complete artifact index` linking every other Markdown file.

Index request, compiler prompt, program, compile notes, interpretation, run log,
inputs, every application prompt/result/status, retry artifacts, hidden results,
and finalizer prompt. Do not link `final.md` to itself.

The finalizer compares its index with the authorized file inventory. The root
then visually lists the actual run directory and checks for missing or broken
relative links. This is a language-level verification pass, not a generated
link manifest.

## File-scope rules

New runs write only inside their allocated run directory. Resume writes only
inside the explicitly named run. Source programs cannot redirect paths.

Application prompts list narrow reads and one write path. In a shared workspace
this is a behavioral boundary, not hard filesystem confinement. Record exact
prompts and use isolation evaluations to expose violations. Never claim that
the artifact layout itself is a sandbox.

No runtime JSON, database, parser output, source map, hash manifest, or
executable script belongs in the run.
