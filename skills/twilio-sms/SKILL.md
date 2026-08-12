---
name: twilio-sms
description: "Twilio SMS CLI: buy/list/keep numbers, send/check messages, credential routing."
metadata:
  short-description: Twilio SMS numbers and messages
---

# Twilio SMS

Use for Twilio phone-number and SMS work: create/buy numbers, list owned numbers, keep/label numbers, send texts, and check inbound/outbound messages.

## Safety

- Never print Account SIDs, auth tokens, API secrets, TOTP codes, or full 1Password item JSON.
- Do not store real phone numbers, SIDs, names, or account-specific item IDs in this skill.
- Use `$one-password` for secret reads. `op` stays tmux-only.
- If desktop 1Password access is needed, unset service-account auth for those commands: `env -u OP_SERVICE_ACCOUNT_TOKEN op ...`.
- Print credential shape only: field present, length, prefix class if useful.
- Public writes or logs: avoid leaking message bodies unless the user asked to read/check SMS.

## Credential Route

1. Check Twilio CLI/profile:
   - `twilio --version` or `npx -y twilio-cli --version`
   - `twilio profiles:list` or `npx -y twilio-cli profiles:list`
2. Check exact env presence only:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - optional API key/secret vars
3. If only partial env exists, search 1Password metadata first.
4. Prefer an item with fields matching:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - optional `TWILIO_FROM_NUMBER`
5. If `op` only sees a restricted vault, retry desktop-backed reads with `env -u OP_SERVICE_ACCOUNT_TOKEN`.
6. Verify auth before any purchase/send:

```bash
curl -sS -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json"
```

## CLI Setup

Twilio CLI profile creation requires account auth token, not just API key creds:

```bash
npx -y twilio-cli profiles:create "$TWILIO_ACCOUNT_SID" \
  --auth-token "$TWILIO_AUTH_TOKEN" \
  --profile default --force --silent
npx -y twilio-cli profiles:use default
```

Use `npx -y twilio-cli` when `twilio` is not installed.

## Numbers

List owned:

```bash
npx -y twilio-cli api:core:incoming-phone-numbers:list \
  --properties phoneNumber,friendlyName,capabilities
```

Search US local SMS-capable inventory:

```bash
npx -y twilio-cli api:core:available-phone-numbers:local:list \
  --country-code US --sms-enabled --voice-enabled --limit 5
```

If the CLI shape is awkward or missing flags, use REST:

```bash
curl -sS -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/AvailablePhoneNumbers/US/Local.json?SmsEnabled=true&VoiceEnabled=true&PageSize=5"
```

Buy one candidate:

```bash
curl -sS -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/IncomingPhoneNumbers.json" \
  --data-urlencode "PhoneNumber=$PHONE_NUMBER"
```

Verify ownership/capabilities after purchase. Twilio JSON uses lowercase keys:

```text
capabilities.sms
capabilities.mms
capabilities.voice
```

Mark numbers the user wants to keep:

```bash
npx -y twilio-cli api:core:incoming-phone-numbers:update \
  --sid "$PHONE_NUMBER_SID" \
  --friendly-name "KEEP - <purpose>"
```

Retention rule: a number is kept while it remains in the Twilio account and billing is healthy. Do not release/delete unless explicitly asked.

## SMS

Send:

```bash
npx -y twilio-cli api:core:messages:create \
  --from "$FROM_NUMBER" \
  --to "$TO_NUMBER" \
  --body "$BODY" \
  -o json
```

Fetch status:

```bash
npx -y twilio-cli api:core:messages:fetch --sid "$MESSAGE_SID" -o json
```

Check inbound to a number:

```bash
npx -y twilio-cli api:core:messages:list \
  --to "$NUMBER" --limit 20 -o json
```

Check outbound from a number:

```bash
npx -y twilio-cli api:core:messages:list \
  --from "$NUMBER" --limit 20 -o json
```

Twilio CLI JSON can return an array for single-resource commands. Parse defensively:

```bash
jq 'if type=="array" then .[0] else . end'
```

## Notes

- International SMS may show an alphanumeric or carrier sender instead of the purchased US number.
- US SMS can be compliance-gated. If sending to US recipients fails, check A2P/10DLC registration state before retrying blindly.
- Trial accounts may restrict recipients.
