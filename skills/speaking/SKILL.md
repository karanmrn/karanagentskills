---
name: speaking
description: "Speaking ops: invites, keynotes, panels, Gmail/calendar, conferences."
---

# Speaking

Use this for Peter's speaking-opportunity workflow.

## Sources

- Repo: `/Users/steipete/Projects/conferences`
- Sheet: `Peter Steinberger Inbounds`
- Sheet URL: https://docs.google.com/spreadsheets/d/1dNt5EjgfgvPoAx5fa-igk681gniCkzL-IZ2FmjFl8fs/edit?gid=0#gid=0
- Main tab: `Invitations`
- Main brief: `/Users/steipete/Projects/conferences/conference-opportunities.md`
- One note per opportunity: `/Users/steipete/Projects/conferences/opportunities/NNN-slug.md`

Use `gog` first for Google data when available:

```bash
gog gmail search 'speaker OR keynote OR panel OR fireside OR conference OR summit after:2026-01-01' --json --no-input
gog gmail read <thread-or-message-id> --json --no-input
gog calendar events primary --time-min 2026-01-01T00:00:00Z --time-max 2026-12-31T23:59:59Z --json --no-input
gog sheets get 1dNt5EjgfgvPoAx5fa-igk681gniCkzL-IZ2FmjFl8fs 'Invitations!A1:Q110' --json --no-input
```

## Scope

Track:

- conferences, summits, retreats, keynotes, panels, firesides, workshops, university talks, high-signal private rooms
- calendar holds that look like speaking commitments
- email invites where Peter expressed interest, declined, or needs to respond

Do not track in the conference list:

- podcasts
- press interviews
- generic networking dinners without a speaking/event ask
- vague intro calls with no event or audience

Talks and firesides are welcome. Do not delete them just because they are not classic conferences.

## Evaluation

Score with these heuristics:

- Audience leverage: developers, founders, AI researchers, senior enterprise buyers/advisors, policy/media only if strategic.
- Role quality: keynote/main stage/fireside > panel > passive attendance.
- Proof: verified email thread, named organizer, calendar invite, public event page, agenda, attendee size.
- Fit: OpenClaw, agents, developer tools, AI-native software, open source, founder story, OpenAI-aligned narrative.
- Logistics: date conflicts, visa, travel, time zone, prep burden, travel/hospitality coverage.
- Risk: platform politics, employer comms approval, geopolitical/compliance concerns, weak organizer quality.

Priority language:

- `accept`: committed or clearly worth doing.
- `strong consider`: high value but needs missing logistics/details.
- `review`: plausible, needs more info.
- `pass`: declined, stale, low leverage, bad fit, or user explicitly said no.

## Verification

Before changing status:

1. Search Gmail for the event name, organizer, contact email, and likely aliases.
2. Read the full thread, not just snippets.
3. Check Google Calendar for matching holds/invites.
4. Treat calendar-only holds as unverified unless email supports them.
5. Preserve Peter corrections: OMR/ORM is not a commitment; do not mark accepted unless Peter explicitly reverses that.

Useful status meanings:

- `CALENDARED`: calendar plus email evidence, or accepted invite.
- `INBOX`: needs response or still open.
- `INBOX / CALENDAR HOLD`: calendar hold exists, but details still need confirmation.
- `PASS`: do not pursue.
- `Done`: declined, stale, or already passed.

## Repo Notes

Per-opportunity files should stay short and structured:

```markdown
# Event Name

- Number: N
- Index: [Conference Opportunities Brief](../conference-opportunities.md)

## Brief

- Date/location:
- Host/ask:
- Format:
- Audience/scale:
- Impact:
- Fit:
- Risks:
- Status:
- Recommendation:
- Sources:
```

When adding an opportunity:

1. Pick next number from `opportunities/*.md`.
2. Add `opportunities/NNN-slug.md`.
3. Add the link to `conference-opportunities.md`.
4. Update the shortlist only if it changes prioritization.
5. Keep podcasts and press out.

## Sheet Sync

Use the sheet headers from `Invitations!A1:Q1`:

`Invitation Name`, `Primary Category`, `Recommendation`, `Date`, `Location`, `Subcategory`, `Geography`, `Recommended Rep`, `Response Status`, `Status`, `Outlet / Event`, `Contact Name`, `Contact Email`, `Topic / Subject`, `Notes`, `Source File`, `From Raw`

Sync rules:

- Main tab should contain conference/speaking opportunities only.
- `Primary Category` can remain `Conference` as the broad bucket, while `Subcategory` explains keynote/panel/fireside/talk/retreat.
- Preserve contact names/emails from existing rows when possible.
- Overwrite stale podcast/press rows if they are present in `Invitations`.
- After writing, re-read the range and verify row count plus no podcast/press name hits.

Use `gog sheets update ... --values-json` for bulk updates. Avoid one-cell micro-edits.
