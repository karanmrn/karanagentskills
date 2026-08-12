# Example Sem run view manifests

These examples are compact, valid version-1 choices for the source trees shown.
They demonstrate recoverable facts, not golden titles, optional nodes, group
boundaries, or emphasis. In every case the artifact inventory, rather than the
node panel list, is the complete file index.

## One imported application, with the application as the result

Source tree, relative to the explicit run root:

```text
request.md
program.md
compile-notes.md
interpretation.md
run.md
applications/001-answer/prompt.md
applications/001-answer/result.md
applications/001-answer/status.md
final.md
```

The program was imported, so there is no `compiler-prompt.md`. The brief
`compile-notes.md` records that fact. The application node itself is the
returned result; a redundant value node is unnecessary.

```json
{
  "kind": "sem-run-view",
  "schemaVersion": "1.0",
  "generatedAt": "2026-07-19T15:30:00Z",
  "run": { "title": "Imported answer", "status": "succeeded", "snapshot": false },
  "artifacts": [
    { "id": "a-request", "path": "request.md", "mediaType": "text/markdown", "role": "request", "title": "Request", "ownerNodeId": "n-request" },
    { "id": "a-program", "path": "program.md", "mediaType": "text/markdown", "role": "program", "title": "Imported program", "ownerNodeId": "n-request" },
    { "id": "a-compile-notes", "path": "compile-notes.md", "mediaType": "text/markdown", "role": "compile-notes", "title": "Import notes", "ownerNodeId": "n-request" },
    { "id": "a-interpretation", "path": "interpretation.md", "mediaType": "text/markdown", "role": "interpretation", "title": "Runtime interpretation", "ownerNodeId": "n-answer" },
    { "id": "a-run", "path": "run.md", "mediaType": "text/markdown", "role": "run-log", "title": "Run log", "ownerNodeId": "n-answer" },
    { "id": "a-prompt", "path": "applications/001-answer/prompt.md", "mediaType": "text/markdown", "role": "application-prompt", "title": "Answer prompt", "ownerNodeId": "n-answer" },
    { "id": "a-result", "path": "applications/001-answer/result.md", "mediaType": "text/markdown", "role": "application-result", "title": "Accepted answer", "ownerNodeId": "n-answer" },
    { "id": "a-status", "path": "applications/001-answer/status.md", "mediaType": "text/markdown", "role": "application-status", "title": "Answer status", "ownerNodeId": "n-answer" },
    { "id": "a-final", "path": "final.md", "mediaType": "text/markdown", "role": "final", "title": "Finalizer report", "ownerNodeId": "n-answer" }
  ],
  "nodes": [
    {
      "id": "n-request",
      "type": "source",
      "title": "Imported request and program",
      "status": "succeeded",
      "emphasis": "context",
      "panels": [
        { "id": "request", "label": "Request", "artifactId": "a-request", "role": "primary", "renderAs": "markdown", "defaultOpen": true },
        { "id": "program", "label": "Program", "artifactId": "a-program", "role": "source", "renderAs": "code" },
        { "id": "import", "label": "Import notes", "artifactId": "a-compile-notes", "role": "explanation", "renderAs": "markdown" }
      ]
    },
    {
      "id": "n-answer",
      "type": "application",
      "title": "Answer",
      "status": "succeeded",
      "emphasis": "primary",
      "ordinal": 1,
      "application": { "directory": "applications/001-answer", "operator": { "kind": "local", "name": "answer" } },
      "panels": [
        { "id": "result", "label": "Result", "artifactId": "a-result", "role": "result", "renderAs": "markdown", "selector": { "kind": "markdown-heading", "heading": "Result" }, "order": 0, "defaultOpen": true },
        { "id": "prompt", "label": "Prompt", "artifactId": "a-prompt", "role": "prompt", "renderAs": "markdown", "order": 1 },
        { "id": "status", "label": "Status", "artifactId": "a-status", "role": "status", "renderAs": "metadata", "order": 2 },
        { "id": "final", "label": "Final report", "artifactId": "a-final", "role": "explanation", "renderAs": "markdown", "order": 3 }
      ]
    }
  ],
  "edges": [
    { "id": "e-request-answer", "from": "n-request", "to": "n-answer", "type": "value", "label": "declared request input" }
  ],
  "groups": [],
  "presentation": {
    "entryNodeIds": ["n-request"],
    "featuredNodeIds": ["n-answer"],
    "resultNodeIds": ["n-answer"]
  },
  "warnings": [
    { "code": "imported-program", "message": "The program was imported; no compiler prompt exists.", "severity": "info", "artifactIds": ["a-program", "a-compile-notes"] }
  ],
  "extensions": {}
}
```

Consumer walk: open the fixed entry point, follow `n-request` to `n-answer`,
render the accepted `Result` section, and use the remaining panels or complete
inventory for provenance. No program parsing is needed. There is one source
application directory, one application node, nine source files, and nine
artifact records.

## Fan-out with a hidden upstream and ordered returns

Source tree:

```text
request.md
program.md
interpretation.md
run.md
applications/001-prepare/prompt.md
applications/001-prepare/result.md
applications/001-prepare/status.md
applications/002-branch-a/prompt.md
applications/002-branch-a/result.md
applications/002-branch-a/status.md
applications/003-branch-b/prompt.md
applications/003-branch-b/result.md
applications/003-branch-b/status.md
final.md
```

The materialized fan-out branches are independently addressable. The shared
preparation is initially hidden, not omitted. The declared return order is B
then A even though their directory ordinals are A then B.

```json
{
  "kind": "sem-run-view",
  "schemaVersion": "1.0",
  "generatedAt": "2026-07-19T16:00:00Z",
  "run": { "title": "Two views", "status": "succeeded", "snapshot": false },
  "artifacts": [
    { "id": "a-request", "path": "request.md", "mediaType": "text/markdown", "role": "request", "title": "Request", "ownerNodeId": "n-request" },
    { "id": "a-program", "path": "program.md", "mediaType": "text/markdown", "role": "program", "title": "Program", "ownerNodeId": "n-request" },
    { "id": "a-interpretation", "path": "interpretation.md", "mediaType": "text/markdown", "role": "interpretation", "title": "Interpretation" },
    { "id": "a-run", "path": "run.md", "mediaType": "text/markdown", "role": "run-log", "title": "Run log" },
    { "id": "a-prepare-prompt", "path": "applications/001-prepare/prompt.md", "mediaType": "text/markdown", "role": "application-prompt", "title": "Prepare prompt", "ownerNodeId": "n-prepare" },
    { "id": "a-prepare-result", "path": "applications/001-prepare/result.md", "mediaType": "text/markdown", "role": "application-result", "title": "Prepared value", "ownerNodeId": "n-prepare" },
    { "id": "a-prepare-status", "path": "applications/001-prepare/status.md", "mediaType": "text/markdown", "role": "application-status", "title": "Prepare status", "ownerNodeId": "n-prepare" },
    { "id": "a-a-prompt", "path": "applications/002-branch-a/prompt.md", "mediaType": "text/markdown", "role": "application-prompt", "title": "Branch A prompt", "ownerNodeId": "n-item-a" },
    { "id": "a-a-result", "path": "applications/002-branch-a/result.md", "mediaType": "text/markdown", "role": "application-result", "title": "Branch A result", "ownerNodeId": "n-item-a" },
    { "id": "a-a-status", "path": "applications/002-branch-a/status.md", "mediaType": "text/markdown", "role": "application-status", "title": "Branch A status", "ownerNodeId": "n-item-a" },
    { "id": "a-b-prompt", "path": "applications/003-branch-b/prompt.md", "mediaType": "text/markdown", "role": "application-prompt", "title": "Branch B prompt", "ownerNodeId": "n-item-b" },
    { "id": "a-b-result", "path": "applications/003-branch-b/result.md", "mediaType": "text/markdown", "role": "application-result", "title": "Branch B result", "ownerNodeId": "n-item-b" },
    { "id": "a-b-status", "path": "applications/003-branch-b/status.md", "mediaType": "text/markdown", "role": "application-status", "title": "Branch B status", "ownerNodeId": "n-item-b" },
    { "id": "a-final", "path": "final.md", "mediaType": "text/markdown", "role": "final", "title": "Final result" }
  ],
  "nodes": [
    {
      "id": "n-request",
      "type": "source",
      "title": "Request",
      "emphasis": "context",
      "panels": [
        { "id": "request", "label": "Request", "artifactId": "a-request", "role": "primary", "renderAs": "markdown" },
        { "id": "program", "label": "Program", "artifactId": "a-program", "role": "source", "renderAs": "code" }
      ]
    },
    {
      "id": "n-prepare",
      "type": "application",
      "title": "Prepare shared value",
      "status": "succeeded",
      "emphasis": "hidden",
      "ordinal": 1,
      "application": { "directory": "applications/001-prepare", "operator": { "kind": "local", "name": "prepare" } },
      "panels": [
        { "id": "result", "label": "Prepared value", "artifactId": "a-prepare-result", "role": "result", "renderAs": "markdown", "selector": { "kind": "markdown-heading", "heading": "Result" } },
        { "id": "prompt", "label": "Prompt", "artifactId": "a-prepare-prompt", "role": "prompt", "renderAs": "markdown" },
        { "id": "status", "label": "Status", "artifactId": "a-prepare-status", "role": "status", "renderAs": "metadata" }
      ]
    },
    {
      "id": "n-item-a",
      "type": "application",
      "title": "Item A",
      "status": "succeeded",
      "emphasis": "primary",
      "ordinal": 2,
      "groupIds": ["g-fanout"],
      "application": { "directory": "applications/002-branch-a", "operator": { "kind": "standard-library", "name": "parable" } },
      "panels": [
        { "id": "result", "label": "Result", "artifactId": "a-a-result", "role": "result", "renderAs": "markdown", "selector": { "kind": "markdown-heading", "heading": "Result" } },
        { "id": "prompt", "label": "Prompt", "artifactId": "a-a-prompt", "role": "prompt", "renderAs": "markdown" },
        { "id": "status", "label": "Status", "artifactId": "a-a-status", "role": "status", "renderAs": "metadata" }
      ]
    },
    {
      "id": "n-item-b",
      "type": "application",
      "title": "Item B",
      "status": "succeeded",
      "emphasis": "primary",
      "ordinal": 3,
      "groupIds": ["g-fanout"],
      "application": { "directory": "applications/003-branch-b", "operator": { "kind": "standard-library", "name": "lyric" } },
      "panels": [
        { "id": "result", "label": "Result", "artifactId": "a-b-result", "role": "result", "renderAs": "markdown", "selector": { "kind": "markdown-heading", "heading": "Result" } },
        { "id": "prompt", "label": "Prompt", "artifactId": "a-b-prompt", "role": "prompt", "renderAs": "markdown" },
        { "id": "status", "label": "Status", "artifactId": "a-b-status", "role": "status", "renderAs": "metadata" }
      ]
    }
  ],
  "edges": [
    { "id": "e-request-prepare", "from": "n-request", "to": "n-prepare", "type": "value" },
    { "id": "e-prepare-a", "from": "n-prepare", "to": "n-item-a", "type": "value", "order": 0 },
    { "id": "e-prepare-b", "from": "n-prepare", "to": "n-item-b", "type": "value", "order": 1 }
  ],
  "groups": [
    { "id": "g-fanout", "title": "Parallel views", "type": "fan-out", "memberNodeIds": ["n-item-a", "n-item-b"], "summary": "Two independent branches over the shared value." }
  ],
  "presentation": {
    "entryNodeIds": ["n-request"],
    "featuredNodeIds": ["n-item-a", "n-item-b"],
    "resultNodeIds": ["n-item-b", "n-item-a"]
  },
  "warnings": [],
  "extensions": {}
}
```

Consumer walk: frame the two featured branches, respect B-then-A return order,
and reveal `n-prepare` on demand to trace both accepted value edges. The three
application directories map to three application nodes. All fourteen source
files have one artifact record even though run-level provenance is left in the
inventory rather than repeated as panels.

## Retry with partial failure and a blocked dependent

Source tree:

```text
request.md
program.md
interpretation.md
run.md
applications/001-recover/prompt.md
applications/001-recover/result.md
applications/001-recover/status.md
applications/001-recover/attempts/001-failure.md
applications/001-recover/attempts/002-prompt.md
applications/002-critic/prompt.md
applications/002-critic/status.md
applications/003-synthesis/prompt.md
applications/003-synthesis/status.md
finalizer-prompt.md
final.md
```

The first application succeeded after a rejected attempt. Its canonical root
`result.md`, not the attempt failure, is the accepted value. An independent
partial return survives even though the critic failed and synthesis was
blocked.

```json
{
  "kind": "sem-run-view",
  "schemaVersion": "1.0",
  "generatedAt": "2026-07-19T16:30:00Z",
  "run": { "title": "Recover then synthesize", "status": "partial", "snapshot": false },
  "artifacts": [
    { "id": "a-request", "path": "request.md", "mediaType": "text/markdown", "role": "request", "title": "Request", "ownerNodeId": "n-request" },
    { "id": "a-program", "path": "program.md", "mediaType": "text/markdown", "role": "program", "title": "Program", "ownerNodeId": "n-request" },
    { "id": "a-interpretation", "path": "interpretation.md", "mediaType": "text/markdown", "role": "interpretation", "title": "Interpretation" },
    { "id": "a-run", "path": "run.md", "mediaType": "text/markdown", "role": "run-log", "title": "Run log" },
    { "id": "a-recover-prompt", "path": "applications/001-recover/prompt.md", "mediaType": "text/markdown", "role": "application-prompt", "title": "Initial recover prompt", "ownerNodeId": "n-recover" },
    { "id": "a-recover-result", "path": "applications/001-recover/result.md", "mediaType": "text/markdown", "role": "application-result", "title": "Accepted recovered value", "ownerNodeId": "n-recover" },
    { "id": "a-recover-status", "path": "applications/001-recover/status.md", "mediaType": "text/markdown", "role": "application-status", "title": "Recover status", "ownerNodeId": "n-recover" },
    { "id": "a-attempt-failure", "path": "applications/001-recover/attempts/001-failure.md", "mediaType": "text/markdown", "role": "attempt", "title": "Rejected first attempt", "ownerNodeId": "n-attempt-1" },
    { "id": "a-retry-prompt", "path": "applications/001-recover/attempts/002-prompt.md", "mediaType": "text/markdown", "role": "attempt", "title": "Retry prompt", "ownerNodeId": "n-attempt-1" },
    { "id": "a-critic-prompt", "path": "applications/002-critic/prompt.md", "mediaType": "text/markdown", "role": "application-prompt", "title": "Critic prompt", "ownerNodeId": "n-critic" },
    { "id": "a-critic-status", "path": "applications/002-critic/status.md", "mediaType": "text/markdown", "role": "application-status", "title": "Critic failure status", "ownerNodeId": "n-critic" },
    { "id": "a-synthesis-prompt", "path": "applications/003-synthesis/prompt.md", "mediaType": "text/markdown", "role": "application-prompt", "title": "Synthesis prompt", "ownerNodeId": "n-synthesis" },
    { "id": "a-synthesis-status", "path": "applications/003-synthesis/status.md", "mediaType": "text/markdown", "role": "application-status", "title": "Synthesis blocked status", "ownerNodeId": "n-synthesis" },
    { "id": "a-finalizer", "path": "finalizer-prompt.md", "mediaType": "text/markdown", "role": "finalizer-prompt", "title": "Finalizer prompt" },
    { "id": "a-final", "path": "final.md", "mediaType": "text/markdown", "role": "final", "title": "Partial final result", "ownerNodeId": "n-recover" }
  ],
  "nodes": [
    {
      "id": "n-request",
      "type": "source",
      "title": "Request",
      "emphasis": "context",
      "panels": [
        { "id": "request", "label": "Request", "artifactId": "a-request", "role": "primary", "renderAs": "markdown" },
        { "id": "program", "label": "Program", "artifactId": "a-program", "role": "source", "renderAs": "code" }
      ]
    },
    {
      "id": "n-attempt-1",
      "type": "event",
      "title": "Rejected first attempt",
      "status": "failed",
      "emphasis": "context",
      "ordinal": 1,
      "groupIds": ["g-retry"],
      "panels": [
        { "id": "failure", "label": "Failure", "artifactId": "a-attempt-failure", "role": "attempt", "renderAs": "markdown" },
        { "id": "retry-prompt", "label": "Retry prompt", "artifactId": "a-retry-prompt", "role": "attempt", "renderAs": "markdown" }
      ]
    },
    {
      "id": "n-recover",
      "type": "application",
      "title": "Recover",
      "status": "succeeded",
      "emphasis": "primary",
      "ordinal": 1,
      "groupIds": ["g-retry"],
      "application": { "directory": "applications/001-recover", "operator": { "kind": "local", "name": "recover" } },
      "panels": [
        { "id": "result", "label": "Accepted result", "artifactId": "a-recover-result", "role": "result", "renderAs": "markdown", "selector": { "kind": "markdown-heading", "heading": "Result" }, "defaultOpen": true },
        { "id": "prompt", "label": "Initial prompt", "artifactId": "a-recover-prompt", "role": "prompt", "renderAs": "markdown" },
        { "id": "status", "label": "Status and attempts", "artifactId": "a-recover-status", "role": "status", "renderAs": "metadata" },
        { "id": "final", "label": "Partial final", "artifactId": "a-final", "role": "explanation", "renderAs": "markdown" }
      ]
    },
    {
      "id": "n-critic",
      "type": "application",
      "title": "Critic",
      "status": "failed",
      "emphasis": "primary",
      "ordinal": 2,
      "application": { "directory": "applications/002-critic", "operator": { "kind": "semantic-judgment", "name": "critic" } },
      "panels": [
        { "id": "prompt", "label": "Prompt", "artifactId": "a-critic-prompt", "role": "prompt", "renderAs": "markdown" },
        { "id": "status", "label": "Failure", "artifactId": "a-critic-status", "role": "status", "renderAs": "metadata", "defaultOpen": true }
      ]
    },
    {
      "id": "n-synthesis",
      "type": "application",
      "title": "Synthesis",
      "status": "blocked",
      "emphasis": "primary",
      "ordinal": 3,
      "application": { "directory": "applications/003-synthesis", "operator": { "kind": "local", "name": "synthesize" } },
      "panels": [
        { "id": "prompt", "label": "Planned prompt", "artifactId": "a-synthesis-prompt", "role": "prompt", "renderAs": "markdown" },
        { "id": "status", "label": "Blocked status", "artifactId": "a-synthesis-status", "role": "status", "renderAs": "metadata", "defaultOpen": true }
      ]
    }
  ],
  "edges": [
    { "id": "e-request-recover", "from": "n-request", "to": "n-recover", "type": "value" },
    { "id": "e-attempt-recover", "from": "n-attempt-1", "to": "n-recover", "type": "retry", "label": "mechanical retry accepted" },
    { "id": "e-recover-critic", "from": "n-recover", "to": "n-critic", "type": "value" },
    { "id": "e-critic-synthesis", "from": "n-critic", "to": "n-synthesis", "type": "control", "label": "unfulfilled: critic failed" }
  ],
  "groups": [
    { "id": "g-retry", "title": "Recover attempts", "type": "retry", "memberNodeIds": ["n-attempt-1", "n-recover"], "collapsedByDefault": false }
  ],
  "presentation": {
    "entryNodeIds": ["n-request"],
    "featuredNodeIds": ["n-recover", "n-critic", "n-synthesis"],
    "resultNodeIds": ["n-recover"]
  },
  "warnings": [
    { "code": "partial-run", "message": "The critic failed and synthesis was blocked; the recovered value is the only returned result.", "severity": "warning", "nodeIds": ["n-critic", "n-synthesis"] }
  ],
  "extensions": {}
}
```

Consumer walk: open the request, traverse the accepted recover value to the
failed critic, then the explicitly unfulfilled control edge to blocked
synthesis. The retry group exposes the rejected attempt separately. Three
application directories map to three application nodes, and all fifteen source
files have one artifact record.

## Active snapshot variation

An active run uses the same shape. Set `run.status` to `running` and
`run.snapshot` to `true`, set `generatedAt` to the observation time, omit
nonexistent final or result artifacts, and allow `resultNodeIds` to be empty.
Keep pending, ready, running, succeeded, failed, and blocked applications as
independent nodes according to observed status. Add a warning and a matching
`view/notes.md` caveat that regeneration is required after the source run
changes. Do not manufacture a final node to make the snapshot appear complete.

## Consistency summary

| Example | Source files / artifacts | Application dirs / nodes | Result IDs |
| --- | ---: | ---: | --- |
| Imported single application | 9 / 9 | 1 / 1 | `n-answer` |
| Fan-out with ordered returns | 14 / 14 | 3 / 3 | `n-item-b`, `n-item-a` |
| Retry and partial failure | 15 / 15 | 3 / 3 | `n-recover` |

For each example a fixed consumer can discover the bundle, render every node
panel, list every source artifact, follow declared edges and groups, and show
ordered returns without opening `program.md` or interpreting Markdown.
