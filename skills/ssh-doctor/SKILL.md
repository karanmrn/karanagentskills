---
name: ssh-doctor
description: "SSH triage: Remote Login, launchd sshd, pre-auth closes, stale sessions."
---

# SSH Doctor

Use when SSH connects then closes before auth, Remote Login seems advertised but unusable, or local/remote Mac SSH needs diagnosis.

## Rules

- Do not print secrets, tokens, full env, or broad secret grep output.
- Validate locally first: loopback failure means server-side sshd/launchd/config; loopback success plus remote failure means network/firewall/filter/listen path.
- Report suspicious config lines before changing `/etc/ssh/sshd_config`.
- Prefer non-interactive SSH:

```bash
ssh -o RequestTTY=no -o RemoteCommand=none HOST 'hostname; id -un'
```

## Baseline

```bash
hostname; id -un; sw_vers
ipconfig getifaddr en0
ipconfig getifaddr en1 2>/dev/null || true
ipconfig getifaddr en7 2>/dev/null || true
sudo systemsetup -getremotelogin
sudo systemsetup -setremotelogin on
sudo launchctl print system/com.openssh.sshd 2>&1 | head -80
sudo launchctl kickstart -k system/com.openssh.sshd
sudo lsof -nP -iTCP:22 -sTCP:LISTEN
nc -vz 127.0.0.1 22
ssh -4 -F /dev/null -o RequestTTY=no -o RemoteCommand=none USER@127.0.0.1 'hostname; id -un'
```

Use `BatchMode=yes` only when password fallback would hang or prompt.

## Config

```bash
sudo sshd -T 2>&1 | egrep -i '^(allowusers|denyusers|allowgroups|denygroups|listenaddress|maxstartups|logingracetime|usepam|passwordauthentication|pubkeyauthentication|authenticationmethods)'
sudo egrep -n '^[[:space:]]*(AllowUsers|DenyUsers|AllowGroups|DenyGroups|Match|MaxStartups|LoginGraceTime|ListenAddress|AuthenticationMethods|UsePAM|PasswordAuthentication|PubkeyAuthentication)\b' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null || true
```

Suspicious:

- `DenyUsers` matching target user
- restrictive `AllowUsers` / `AllowGroups`
- `Match` block accidentally applying
- tiny `MaxStartups`
- tiny `LoginGraceTime`
- `ListenAddress` missing target interface

## Logs

```bash
sudo log show --last 30m --predicate 'process == "sshd" OR process == "launchd"' --style compact | tail -160
```

Important Mac symptom:

- client: `kex_exchange_identification: Connection closed by remote host`
- server log: `Could not create new instance of inetd service: 67: Too many processes`
- `launchctl print system/com.openssh.sshd`: high `copy count`
- many `sshd-session: USER` processes parented by PID 1

This means launchd accepted TCP but refused to spawn more sshd inetd copies.

## Stale sshd-session Fix

Inspect first:

```bash
sudo launchctl print system/com.openssh.sshd 2>&1 | egrep 'active count|copy count|state =|last exit code|runs ='
ps -axo pid,ppid,uid,user,state,lstart,etime,comm,args | awk '/sshd-session:/ && !/awk/ {print}'
sudo lsof -nP -c sshd-session -iTCP 2>/dev/null | head -120
```

If stale sessions are clearly stranded and blocking new SSH, terminate by selected command-line match:

```bash
ps -axo pid=,args= | awk '/sshd-session: / && !/awk/ {print $1}' | xargs sudo kill -TERM
sleep 2
ps -axo pid=,args= | awk '/sshd-session: / && !/awk/ {print}'
```

If `TERM` leaves blockers, re-check ownership and active shells before using `KILL`.

## Firewall

Only after loopback works but remote fails:

```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep -i ssh -A2 -B2 || true
sudo pfctl -sr 2>/dev/null | head -80
sudo pfctl -si 2>/dev/null | head -80
```

Also check listen address and target interface:

```bash
ifconfig | awk '/^[a-z0-9]+:/{iface=$1; sub(":","",iface)} iface ~ /^en[0-9]+$/ && /inet / {print iface, $2}'
sudo lsof -nP -iTCP:22 -sTCP:LISTEN
```

## OP Profile Block

If asked to ensure `~/.profile` has a Codex-managed `OP_SERVICE_ACCOUNT_TOKEN` copied from another host:

- verify exact variable/markers without printing value
- copy only the matching line/block
- redirect through a `chmod 600` temp file
- never echo the token

Presence check:

```bash
awk 'BEGIN{b=0;e=0;x=0} /BEGIN Codex-managed OP_SERVICE_ACCOUNT_TOKEN/ {b=1} /END Codex-managed OP_SERVICE_ACCOUNT_TOKEN/ {e=1} /^[[:space:]]*(export[[:space:]]+)?OP_SERVICE_ACCOUNT_TOKEN=/ {x=1} END{print "marker_begin", b; print "marker_end", e; print "exact_var", x}' ~/.profile
```

Append from remote host:

```bash
tmpfile=$(mktemp /tmp/codex-op-token.XXXXXX)
chmod 600 "$tmpfile"
ssh -o RequestTTY=no -o RemoteCommand=none HOST 'awk '\''/^[[:space:]]*(export[[:space:]]+)?OP_SERVICE_ACCOUNT_TOKEN=/ {print; exit}'\'' ~/.profile' > "$tmpfile"
if [ -s "$tmpfile" ]; then
  {
    printf '\n# BEGIN Codex-managed OP_SERVICE_ACCOUNT_TOKEN\n'
    sed -n '1p' "$tmpfile"
    printf '# END Codex-managed OP_SERVICE_ACCOUNT_TOKEN\n'
  } >> ~/.profile
fi
rm -f "$tmpfile"
```

## Closeout

Report:

- root cause
- exact commands changed
- validation output, redacted as needed
- whether remote should retry
