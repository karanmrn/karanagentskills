---
name: release-tweets
description: "Release tweets: draft/copy/post from changelog, tags, npm/appcast, artifacts."
---

# Release Tweets

Use when the user asks for a release tweet, launch tweet, X announcement, release thread, changelog-to-tweet rewrite, or social copy for a shipped version. This skill is about release copy, not cutting the release.

## Ground The Copy

- Verify the release target before writing confident copy:
  - read the relevant `CHANGELOG.md` section or GitHub release notes
  - check the tag/release/npm/appcast/artifact state that applies to the project
  - distinguish `Unreleased`, beta/prerelease, stable, hotfix, and correction releases
- Do not say a feature shipped only because it is in the top changelog block. Confirm the tag/release/package evidence when available.
- Lead with user-visible wins: features, integrations, workflow improvements, install/update reliability, security fixes.
- Avoid leading with CI, coverage, validation, refactors, internal migrations, or release mechanics unless that is the actual story.
- If evidence is incomplete, say what is unverified and draft with softer wording.

## Launch Tweet Shape

- One standard tweet under 280 characters, with room for one URL.
- Typical format:
  - product + version
  - blank line
  - 3-4 compact emoji-led feature bullets
  - blank line
  - one short punchline
  - release/changelog URL
- Use emoji bullets by default for launch tweets. Pick clear, low-noise emoji that match the feature or product; skip only when the user asks for plain text or the release is incident-style.
- Tone: high-signal, compact, confident, a little dry when earned. Not corporate.
- One joke max. Let the feature bullets do the work.
- Put the release/changelog URL at the end.
- Count final raw characters before presenting it as ready to post.

## Beta, Hotfix, Correction

- Beta/prerelease:
  - make beta status explicit
  - avoid implying stable promotion
  - phrase as "beta N", `VERSION-beta.N`, or "preview" as appropriate
- Hotfix/correction:
  - be direct and accountable
  - state what slipped, what is fixed, and the new version
  - skip jokes unless the user asks for a lighter tone

## Threads

- First agree on the generic launch tweet.
- Then write follow-ups one at a time. When the user says `next`, provide only the next reply.
- Each follow-up should focus on one feature or user workflow.
- Include a docs/release URL for the specific feature when available.
- Avoid repeating the version in every reply when the thread context already has it.
- Good follow-up length: 160-220 raw characters. Hard cap: 280.

## Posting And Clipboard

- Draft by default. Do not post to X/Twitter unless the user explicitly asks.
- If asked to copy, use `pbcopy` on macOS and report that it is copied.
- If asked to post from Peter's setup, prefer the local `bird`/`xurl` workflow if available, then verify the posted URL.
- Never invent media. If the user wants media, use an existing release screenshot/asset or ask for/generate one separately.

## Quality Pass

Before final:

- Character count under 280 for each tweet.
- Exact version string and channel.
- Release URL included when requested or expected.
- No unverified claims.
- No more than 3-4 emoji-led bullets in the launch tweet.
- Peter-style concise language; trim filler before trimming facts.

## Examples

```text
OpenClaw 2026.4.20 beta 1

🐳 Docker install/update smoke
🖥️ Parallels upgrade checks
🔧 Package verification tightened

Beta first. Stable after the gauntlet.
<release link>
```

```text
RepoBar 0.5.0 is live

📋 GitHub refs from your clipboard
🔎 Issue, PR, and commit previews
🟢 Open/closed/merged at a glance
🔒 No Accessibility permission needed

Tiny bar, much less mystery.
<release link>
```

```text
Packaging issue in 2026.4.20-beta.1.

2026.4.20-beta.2 fixes install/update verification. No tag rewrites; beta moves forward.

Upgrade with the beta channel.
<release link>
```
