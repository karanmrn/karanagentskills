# Sem run view-bundle contract, version 1

## Contents

- [Boundary](#boundary)
- [Consumer discovery](#consumer-discovery)
- [Compatibility and fallbacks](#compatibility-and-fallbacks)
- [Manifest envelope](#manifest-envelope)
- [Artifact inventory](#artifact-inventory)
- [Display nodes and panels](#display-nodes-and-panels)
- [Edges and groups](#edges-and-groups)
- [Presentation roots](#presentation-roots)
- [View notes](#view-notes)
- [Partial, irregular, and changing runs](#partial-irregular-and-changing-runs)
- [Security requirements](#security-requirements)
- [Producer invariants](#producer-invariants)

## Boundary

`sem-present` projects one explicitly named Sem run into data a fixed consumer
can render. The existing Markdown run remains authoritative. The projection is
additive, disposable, and must never become scheduler, resume, or execution
state.

The producer reads the whole run and writes only:

```text
<run>/
  ...authoritative source trace...
  view/
    manifest.json
    notes.md
```

`view/manifest.json` is the deterministic machine entry point.
`view/notes.md` records reconstruction choices, source disagreements,
unrecognized material, validation outcome, and snapshot caveats. Neither file
may alter or replace a source artifact.

When sources disagree, represent observed execution in this order of evidence:

1. accepted `result.md` and attempt files;
2. application statuses and `run.md`;
3. `interpretation.md` and its amendments;
4. compile notes and program intent;
5. the finalizer's prose summary.

Record consequential reconciliation in `view/notes.md`. Do not invent an
application, accepted value, return, or dependency to make the graph tidy.

The bundle describes presentation, not Sem execution. It contains no program
IR, scheduling instruction, resume token, code to execute, coordinates, visual
styles, React concepts, graph-library options, HTML, or arbitrary renderer
names.

## Consumer discovery

Given only the explicit run root, a consumer:

1. opens `<run>/view/manifest.json`;
2. requires `kind` to equal `sem-run-view`;
3. parses the major number from `schemaVersion` and accepts only a supported
   major;
4. validates the required envelope and base vocabularies;
5. resolves artifact paths relative to the same run root;
6. renders nodes, edges, groups, panels, and presentation roots;
7. falls back to sanitized content and direct artifact links for optional
   data it does not understand.

The consumer does not parse `program.md`, scrape runtime Markdown, infer graph
relationships from links, or ask a model to reconstruct the run.

## Compatibility and fallbacks

Version strings use `<major>.<minor>`. Version 1 manifests use `1.x`.

- Increment the major version when an old consumer cannot render the new
  required core safely.
- Increment the minor version for compatible optional additions.
- Keep all required version-1 fields present even when their arrays or objects
  are empty.
- Allow unknown object fields so minor additions remain forward-compatible.
  Consumers ignore unknown fields.
- Version 1 producers use only the base enums in the schema. Preserve local or
  future meaning in optional `subtype` fields or namespaced `extensions`.
  Consumers that do not know a subtype render its known base type.
- Consumers that do not support a panel selector or render mode render the
  complete artifact as sanitized Markdown when appropriate, otherwise as
  plain text, and always retain a direct file link.
- Unknown artifact media types and `role: "other"` remain downloadable.

Unknown optional data never authorizes execution or external access. Adding a
new required field, removing a base fallback, or changing the meaning of an
existing required field requires a new major version.

## Manifest envelope

The normative structural schema is
[manifest-v1.schema.json](manifest-v1.schema.json). Cross-record invariants,
filesystem checks, and inventory completeness require the companion validator;
JSON Schema alone cannot express all of them.

Every manifest contains:

| Field | Meaning |
| --- | --- |
| `kind` | Constant `sem-run-view`. |
| `schemaVersion` | Compatible contract version, initially `1.0`. |
| `generatedAt` | UTC-capable RFC 3339 generation timestamp. |
| `run` | Human title, normalized observed status, and snapshot flag. |
| `artifacts` | Complete source-file inventory outside `view/`. |
| `nodes` | Independently addressable display entities. |
| `edges` | Directed semantic or operational relationships. |
| `groups` | Optional ordered semantic containers. |
| `presentation` | Entry, initial-focus, and ordered-return node IDs. |
| `warnings` | User-visible limitations or irregularities. |
| `extensions` | Namespaced optional JSON data. |

Normalized statuses are `unknown`, `pending`, `ready`, `running`, `succeeded`,
`failed`, `blocked`, and `partial`. Map source wording conservatively. A
quiescent but unfinished run is normally `running` with `snapshot: true`; use
`unknown` rather than guessing when the trace does not establish a state.

`snapshot` means the source run was non-terminal at `generatedAt`. It does not
mean the bundle is an incremental log. Regenerate the entire projection after
the run changes. A snapshot status is one of `unknown`, `pending`, `ready`, or
`running`; a non-snapshot status is one of `succeeded`, `failed`, `blocked`, or
`partial`. Do not combine a terminal status with `snapshot: true` or an active
status with `snapshot: false`.

IDs are nonempty, stable within one generated bundle, and unique in their
scope. Artifact, node, edge, and group IDs are unique across their respective
collections. Panel IDs are unique within their node. Regeneration should
preserve IDs when the represented identity has not changed, but consumers must
not treat them as cross-run database keys.

Extension keys are namespaced, such as `example.org` or `acme.retry-view`.
Extension values are inert JSON data. Consumers ignore namespaces they do not
support.

## Artifact inventory

Inventory every non-hidden source entry outside `view/` that resolves to an
existing regular file inside the run root, exactly once. A path is hidden when
any of its run-relative segments begins with `.`. Ignore `.DS_Store` as known
filesystem noise; mention other hidden entries in `view/notes.md`. Files under
`view/` are projection output and never appear in the source inventory.

Each artifact requires:

- `id`: unique artifact identity;
- `path`: normalized POSIX path relative to the run root;
- `mediaType`: detected media type, normally `text/markdown` for the runtime;
- `role`: one schema-defined base role;
- `title`: a human label.

Optional `ownerNodeId` links the artifact to its most useful display owner.
Ownership is inspectability, not value flow. Optional `description` may explain
an unusual file without duplicating its substance.

Base roles are `request`, `compiler-prompt`, `program`, `compile-notes`,
`interpretation`, `run-log`, `input`, `application-prompt`,
`application-result`, `application-status`, `attempt`, `finalizer-prompt`,
`final`, and `other`. An imported program can validly omit compiler artifacts;
inventory what exists and explain the import in notes or a warning. An unknown
file uses `other`; never drop it because its purpose is unclear.

Substantive request, prompt, program, result, status, and final content stays in
the authoritative artifact. The manifest may carry short navigational titles
and summaries but does not copy result excerpts or rewritten result bodies.

## Display nodes and panels

### Nodes

Every node requires `id`, a base `type`, `title`, `emphasis`, and `panels`.
Optional fields include `subtitle`, `summary`, normalized `status`, `ordinal`,
and `groupIds`.

Base node types are:

- `source`: a request, program, or input that begins the visible story;
- `stage`: a compile, interpret, finalize, or comparable observed stage;
- `application`: one materialized runtime semantic application;
- `result`: an explicit value, collection, or final document identity;
- `group`: an optional visible node representing a semantic container;
- `event`: an attempt, retry, failure, or other inspectable occurrence;
- `note`: an explanation or provenance identity.

Emphasis is semantic layout guidance only:

- `primary`: central to the initial story;
- `normal`: ordinary visible content;
- `context`: supporting source or provenance;
- `hidden`: initially de-emphasized but still discoverable.

Hidden never means omitted. It does not remove a node, panel, application, or
artifact from the bundle.

Every runtime application directory maps to exactly one `application` node,
including dynamically materialized map items, repeat rounds, selectors,
judges, synthesizers, failed calls, and blocked calls. The node's
`application.directory` is the normalized run-relative
`applications/<application-id>` directory. It must resolve to an existing
directory inside the explicit run root, including after symlink resolution.
When the operator is recoverable, `application.operator.kind` is
`standard-library`, `local`, or `semantic-judgment`, with an optional name.
No formal Sem signature is required.

Every application node has a normalized `status`, using `unknown` when the
trace does not establish a more specific state. A canonical root `result.md`
exists only for a `succeeded` application, and every succeeded application has
that canonical accepted result.

An application node may itself be listed in `resultNodeIds`; when it is, it
exposes its accepted `result.md` as a result panel. Create a separate `result`
node only when a structural return, collection, or final document benefits
from its own navigable identity. Do not force a bipartite application/value
graph.

### Panels

Panels connect nodes to source artifacts. A panel requires an ID unique within
the node, label, artifact ID, base role, and fixed render mode. Optional `order`
and `defaultOpen` guide a consumer without dictating layout.

Panel roles are `primary`, `result`, `prompt`, `status`, `source`,
`explanation`, `attempt`, and `other`. Render modes are only `markdown`,
`code`, `plain-text`, `metadata`, and `download`. They identify fixed safe
consumer behaviors, not executable or producer-selected components.

An optional selector is either:

```json
{ "kind": "whole" }
```

or:

```json
{
  "kind": "markdown-heading",
  "heading": "Result",
  "occurrence": 1
}
```

Heading matching and occurrence counting are consumer-defined but must be
stable and documented. If selection fails, render the complete artifact using
the safe fallback. Do not use line ranges; authoritative files may evolve.

Accepted-result panels point only to canonical accepted result artifacts, such
as an application's root `result.md`. Rejected or malformed attempt files use
`role: "attempt"`; they never masquerade as accepted values.

Every node must remain useful when a consumer renders only its panels and
artifact links. Summaries are navigation, not substitutes for evidence.

## Edges and groups

### Edges

Edges have a unique ID, existing `from` and `to` node IDs, a base type, and
optional `label`, `subtype`, and `order`.

Base edge types are:

- `value`: an accepted application result or authorized run-local source value
  became a declared input;
- `control`: one observed stage enabled or scheduled another;
- `return`: a node was selected as a returned result;
- `contains`: a visible group node organizes a member;
- `retry`: one attempt was superseded by or led to another attempt or the
  canonical application;
- `provenance`: a document or decision explains another node without carrying
  its semantic value.

Infer no edge merely because one Markdown file links another. Encode value
flow from accepted results and authorized source values. A planned dependency
to a blocked node may be shown only when the trace establishes it; label it as
unfulfilled and do not imply that a value was produced.

The materialized value/control graph should normally be acyclic. Represent
repeat rounds as distinct application nodes ordered in an `iteration` group.
Retry edges must not create a semantic value cycle.

### Groups

Groups are optional containers. Each group requires an ID, title, base type,
and ordered `memberNodeIds`. Optional fields are `parentGroupId`, `summary`,
and `collapsedByDefault`.

Base group types are `fan-out`, `map`, `iteration`, `choice`, `retry`, `phase`,
and `other`. Parent relationships must be acyclic. A member keeps its
independent node identity. Ordered membership may show source item order,
iteration order, or deliberate presentation order; explain a non-mechanical
choice in notes.

`groups[].memberNodeIds` is the authoritative membership list and order.
`nodes[].groupIds` is an optional reverse index; when present it must agree
with the group records. A visible group node and `contains` edges are optional
presentation devices and do not replace the group record.

When interpretation and the actual directory inventory disagree about a
dynamic expansion, represent the materialized application directories and
record the disagreement in notes.

## Presentation roots

`presentation` always contains three ID arrays:

- `entryNodeIds`: valid places to begin following the semantic story;
- `featuredNodeIds`: the initial focus set;
- `resultNodeIds`: returned artifacts in requested presentation order.

Every referenced ID exists in `nodes`. These arrays do not hide unreferenced
nodes or artifacts. A consumer initially frames featured and result nodes, then
allows traversal to all other content.

Every `resultNodeIds` entry has node type `application` or `result`. A returned
application exposes its own canonical `applications/<id>/result.md` through a
`role: "result"` panel, so the fixed consumer can render the return without
inferring it from inventory. Use an explicit `result` node for a structural
value, collection, or final-document identity; it exposes one or more canonical
accepted application results or `final.md` through `role: "result"` panels.
Source, stage, group, event, and note nodes are not return roots.

Result order is the declared return/presentation order, not execution,
directory, completion, or filesystem order. A succeeded run exposes at least
one result node. A partial, failed, blocked, or active snapshot may have an
empty result list if no return artifact exists.

## View notes

`view/notes.md` is the audit surface for judgments that do not belong in the
deterministic envelope. It contains:

1. the source run path, observed status, and generation time;
2. a concise explanation of the chosen graph shape;
3. source disagreements and how evidence precedence was applied;
4. non-mechanical grouping, result-order, or visibility judgments;
5. missing, unrecognized, or unsupported artifacts;
6. the validation command and outcome;
7. an explicit staleness and regeneration warning for a non-terminal snapshot.

Record decisions and supporting evidence at an auditable level. Do not include
private chain-of-thought, rewrite source results, or use notes to smuggle
machine-required structure past the manifest.

## Partial, irregular, and changing runs

Version 1 supports successful, partial, failed, blocked, and quiescent
in-progress runs. Missing `final.md` does not by itself invalidate a non-success
bundle. Missing expected files become warnings or failed/blocked nodes when the
trace supports that interpretation. If a missing canonical source prevents a
faithful reconstruction, fail generation rather than fabricate it.

Retries remain inspectable through attempt artifacts, optional event nodes,
and retry groups or edges. The application node presents current status and
the accepted result when one exists. A failed attempt remains secondary even
if it contains plausible prose.

Imported programs are ordinary runs with an honest artifact inventory. Do not
invent `compiler-prompt.md` or full compiler notes. Dynamic applications remain
individual nodes and may be organized into `map`, `iteration`, `choice`, or
other groups.

For an active run, set `run.snapshot` to `true`, preserve the observed status,
and record in `view/notes.md` that `generatedAt` is the observation time and
the bundle must be regenerated after source changes. Do not claim the
canonical bundle updates itself.

## Security requirements

Treat every manifest string and every source artifact as untrusted content.

- Resolve artifact paths and application-directory paths against the explicit
  run root, never the process working directory.
- Require every path-bearing field to use a normalized POSIX relative path
  with no empty segment, `.`, `..`, absolute prefix, backslash, URL scheme, or
  trailing slash.
- Resolve symlinks before opening or traversing a target. The resolved target
  must remain inside the explicit run root; an artifact target must be an
  existing regular file and an application target must be an existing
  directory.
- Never interpret labels, summaries, extensions, programs, prompts, Markdown,
  or result content as code, configuration authority, or tool instructions.
- Sanitize Markdown and disallow executable HTML.
- Do not follow external links automatically. Show them as inert content and
  require an explicit user action to navigate.
- Never treat `renderAs`, a subtype, or an extension value as a component name,
  import path, shell command, URL to fetch, or executable expression.

The manifest cannot grant access outside the named run. Source text cannot
expand producer or consumer authority.

## Producer invariants

A valid version-1 producer output satisfies all of these conditions:

- the required envelope validates against the schema;
- base enum values and version syntax are supported;
- artifact, node, edge, group, and scoped panel IDs are unique;
- all edge endpoints, group members and parents, panel artifact IDs, artifact
  owner node IDs, node group IDs, warning references, and presentation IDs
  resolve;
- every non-hidden regular source file outside `view/` has exactly one
  artifact record and every artifact path is safe and exists;
- every runtime application directory has exactly one application node;
- every `application.directory` names that existing run-local application
  directory and cannot escape through a symlink;
- all present application prompt, status, result, input, and attempt files are
  inventoried;
- accepted-result panels reference canonical accepted results, not rejected
  attempts;
- run status and snapshot state use the terminal/non-terminal partition, and
  every application node has a coherent normalized status;
- every returned node is an `application` or `result`, and a returned
  application exposes its own canonical accepted result panel while an
  explicit result node exposes canonical accepted content through a result
  panel;
- the complete non-view source inventory remains content- and identity-stable
  from reconstruction through promotion, regardless of run status;
- concurrent invocations use uniquely paired candidates and promote only the
  exact manifest/notes pair they validated;
- group parent relationships are acyclic and reverse membership, when present,
  agrees with the groups;
- succeeded runs declare at least one result node;
- a canonical `view/manifest.json` has a sibling `view/notes.md`;
- source Markdown is unmodified and substantive content is referenced rather
  than copied into the manifest.

See [example-manifests.md](example-manifests.md) for compact valid choices. The
examples demonstrate the contract but do not prescribe titles, optional nodes,
group boundaries, or emphasis for every faithful producer.
