---
name: macbook-metrics-setup
description: 'Replicate the macbook-metrics setup on any Mac — a local, always-on system-metrics collector (CPU, GPU, RAM, disk, network, battery, thermals) built as a Swift CLI, run by launchd every 60s, stored in SQLite, and backed up to a private GitHub repo. Use when someone wants long-term Mac performance tracking, asks how macbook-metrics works, or wants to set up the same monitoring on a new machine. Differentiator: covers the full architecture and setup ideology, not day-to-day querying of an existing install.'
---

# MacBook Metrics Setup

How to build a low-overhead, long-term Mac metrics collector you fully own.
No cloud, no telemetry, no accounts — one binary, one SQLite file, two
launchd jobs, one private GitHub repo.

## Ideology (read this before building)

1. **Local-only and deterministic.** The collector never makes network
   calls, never uses an LLM, never sends analytics. Anyone should be able
   to read the code and predict exactly what it writes.
2. **Data lives outside the repo** in
   `~/Library/Application Support/<project>/` so reinstalls and git
   operations never touch measurements.
3. **Low overhead is a hard requirement.** One sample per minute, release
   build, `LowPriorityIO` — the monitor must never become the load.
4. **Undocumented reads stay nullable and fail loudly.** GPU utilization
   and SMC temperature reads use private interfaces that can break on any
   macOS update; store them as nullable columns and surface errors,
   never fake values.
5. **Decisions are written down.** Every architectural choice gets an ADR
   in `docs/adr/`; every schema change gets a numbered SQL file in
   `docs/database/`. Agents and humans follow the ADRs as contracts.
6. **Per-process tracking is opt-in.** System-wide collection is the
   default; monitoring a specific app (e.g. an Electron IDE) is a
   separate, isolated collector added only via its own ADR.

## Repo structure

```
Sources/<ProjectLib>/     # samplers, SQLite storage, report generation
Sources/<project-cli>/    # thin CLI: collect | doctor | report
launchd/                  # plist templates with __PLACEHOLDER__ tokens
scripts/                  # install.sh, uninstall.sh, sync.sh
docs/adr/                 # numbered architecture decision records
docs/database/            # numbered SQL migrations
backups/                  # git-tracked SQLite snapshots (written by sync)
```

Swift + SwiftPM is the natural fit (native IOKit/Mach APIs, zero
dependencies), but the architecture works in any compiled language.

## Data collection

- Sample **system-wide** CPU %, GPU %, memory (used/wired/compressed/
  pressure), swap, disk capacity + IO byte/op counters, network byte/packet
  counters, battery, thermal state, temperatures, fan RPM.
- Store cumulative OS counters (disk/network) as **per-interval deltas**.
- One row per minute into SQLite (WAL mode). A year is only ~500k rows —
  add a 15-minute rollup table for fast long-range reports.
- CLI verbs: `collect` (one sample + exit), `doctor` (print a live reading,
  fail loudly on broken samplers), `report --hours N` (text summary).

## The two launchd jobs

Both are user LaunchAgents in `~/Library/LaunchAgents/` — no root, no
daemon. Templates live in the repo; `install.sh` fills in placeholders.

**1. Collector** — runs the binary with `collect` every 60 seconds:
`RunAtLoad true`, `StartInterval 60`, `ProcessType Background`,
`LowPriorityIO true`, stdout/stderr to `~/Library/Logs/<project>/`.
The process runs for under a second and exits; launchd is the scheduler
(`launchctl list` showing PID `-` with status `0` is healthy).

**2. GitHub sync** — runs `scripts/sync.sh` every 3 hours
(`StartInterval 10800`), which:

```bash
# snapshot safely while the DB is live, then normalize for git
sqlite3 "$db_path" ".backup '$tmp'"
sqlite3 "$tmp" 'PRAGMA journal_mode=DELETE;'   # fold WAL into one file
mv -f "$tmp" backups/metrics.sqlite3
# commit ONLY the backups path, skip if unchanged, push to a PRIVATE repo
git add backups && git commit -m "Backup metrics database $(date '+%Y-%m-%d %H:%M')" -- backups
git push origin HEAD
```

Never copy a live WAL database with `cp` — always `sqlite3 .backup`.
Keep the repo private: metrics reveal your daily activity patterns.

## install.sh pattern

```bash
swift build -c release
# run the binary from Application Support, NOT the repo build dir,
# so rebuilds/branch switches never break the running job
install -m 755 .build/release/<project> "$data_dir/bin/"
install -m 644 launchd/<label>.plist ~/Library/LaunchAgents/
sed -i '' -e "s|__EXECUTABLE__|$binary|" ... "$agent_path"   # fill placeholders
plutil -lint "$agent_path"                                    # validate before loading
launchctl bootout "gui/$UID" "$agent_path" 2>/dev/null || true  # idempotent reinstall
launchctl bootstrap "gui/$UID" "$agent_path"
```

`uninstall.sh` is the reverse: bootout both agents, remove the plists.
Use a reverse-DNS label like `com.<yourname>.<project>`.

## Verify the install

```bash
launchctl list | grep <project>          # exit status 0 = last run OK
sqlite3 "$db" "SELECT datetime(MAX(timestamp),'unixepoch','localtime') FROM raw_samples;"
# must be under a minute old; also run the doctor verb
```

If samples stall: check `~/Library/Logs/<project>/stderr.log` first.

## Optional: isolated per-app monitor

To watch one app (e.g. an Electron IDE with memory leaks), add a separate
opt-in collector with its own schema, install script, and ADR. Find the
app's processes by bundle path (never by name substring), read per-process
CPU/RSS/disk-IO via `proc_pid_rusage`/`proc_pidinfo` — cheap, no root —
and never spawn `ps` in a loop (that is itself a known lag source).
