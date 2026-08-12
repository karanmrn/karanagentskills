---
name: pull-requests
description: Describes how to write pull/merge requests. Use when asked to write or edit a pull request or merge request description. This skill is not relevant to commit messages.
---

# Pull Request + Merge Request Style Guide

## Overview

A good pull request description is a Markdown document that tells the story of the accompanying git diff. It is intended for human consumption and should use plain language, read clearly and be easy to follow.

## When to Use

Use this skill any time you are tasked with creating a pull request on GitHub. The output will be a markdown document that follows the style guide and meets the accompanying verification.

## Structure

A good pull request tells the story of the change and is intended to add color and context that is not or cannot be conveyed in the source code.

It should aim to be concise and use paragraphs and prose where appropriate rather than bullet points to improve readability and tell the story. Bullet points can be used for lists when semantically appropriate.

Code examples and diagrams (using mermaid) are preferred over prose to communicate your message.

It should use the following structure and include a paragraph on each topic.

 1. Detail the problem the change is solving. Reference issues, PRs or documents if relevant.
 2. Explain the solution and how it solves the problem.
 3. Explain how the reader can manually verify the change. e.g. give a code example or a command
    to run locally.
 4. Document the testing strategy when applicable.
 5. Document any changes to documentation or READMEs that cover the changes.
 6. Document any follow up code changes required.

Any sections that are not relevant should be omitted.

## Style guide

It is important to follow these rules when writing a pull request description.

### At all times keep the use of language simple. Use plain English

**Good**: Clear

> We've updated the `readFile()` method to support streaming data so that the caller can read a file without buffering content into memory.

**Bad**: Verbose and technical jargon

> The `readFile()` function has an overload that when used returns a `ReadableStream()` object that emits chunks of `UInt8Array` type that can be used by the caller to stream bytes instead of base64 strings which are held in memory.

### Avoid technical terms or jargon

**Good**:

> The daemon now flushes pending writes before it tears down the mount.

**Bad**:

> The daemon now performs a synchronous fsync barrier against the underlying inode cache before invoking the FUSE unmount ioctl.

### Never use acronyms, always use the full word unless it's extremely common like API, RPC or HTTP

**Good:**

> We've updated the durable object (DO) to use RPC to reduce the time-to-first-byte (TTFB)

**Bad:**

> We've updated the DO to use RPC to reduce TTFB.

### Keep it high level

Describe what the code cannot. Architecture, design decisions, important trade-offs are the important details. Do not attempt to describe what the code is doing, the code itself can do that.

**Good:**

> This change extends the same call site to accept a name option. When set, the SDK provisions a named Cloudflare Tunnel under a zone the user controls and binds <name>.<zone> to the local port. Quick and named tunnels share the same entry point, the same TunnelInfo shape (now a discriminated union keyed on name), and the same destroy() semantics

**Bad:**

> This change extends `tunnels.ts` to update the `get()` method to accept a name option `{ name: "bill" }`. When set, the SDK provisions a named Cloudflare Tunnel via `cloudflared` running via `Bun.spawn()` under a zone the user controls and binds <name>.<zone> to the local port. Quick and named tunnels share the same entry point `sandbox.tunnels`, the same `TunnelInfo` shape (now a discriminated union keyed on name `NamedTunnelInfo | QuickTunnelInfo`), and the same destroy() semantics.

### Use American English spelling at all times

e.g. color instead of colour.

### Never refer to agent conversations or chat history when writing plans, documentation or commit/pull requests

**Good:**

> Further work will be required to update the remaining file methods to support streaming data.

**Bad:**

> Streaming in `writeFile()` will be implemented as part of the P2 plan to update the remaining methods.

### Never reference local files or documents that are not contained within the commit history in the repository

**Good:**

> Further work will be required to update the remaining file methods to support streaming data.

**Bad:**

> The plan for the `writeFile()` changes as detailed in P2 in PLAN.md

# Markdown

Format the pull request using Github flavored markdown, do not use hard line breaks. Use US English spelling.

 - Use code fences to wrap class, variable names etc when referencing code.
 - Use `<detail>` elements to hide verbose code examples or log output.

## Anti-Patterns to Avoid

| Anti-Pattern                            | Problem                                                                                             | Fix                                                                                                           |
| --------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Including lists of code changes         | The description is always accompanied by a diff there is no need to include a list of file changes. | Remove the list and include any relevant filenames as part of the implementation overview.                    |
| Overuse of headings                     | Makes the description overly verbose. It is intended to be short and concise.                       | Remove the headings in favor of sequential paragraphs. Use bold characters if a section is absolutely needed. |
| Referencing agent conversation or files | The reviewer has no context about these conversations so they are irrelevant.                       | Ensure the context is covered in the pull request and the text is comprehensible on it's own.                 |

## Verification

After completing any pull request description:

Review the content and ask "can this be shorter?". Then make it shorter. Do this twice. Use code blocks and diagrams where appropriate to simplify prose.

Finally, ensure the folowing requirements are met:

 - [ ] Code braces are used to wrap code e.g. `req.fetch()` or `MyClass`.
 - [ ] There are no heading elements in the document.
 - [ ] There are no lists of file changes in the document.
 - [ ] There are no references to agent conversation or files in the document.
 - [ ] There are no references to files that are not part of the git history.
 - [ ] There are no empty sections, or paragraphs that say nothing useful e.g. "There are no documentation changes"
