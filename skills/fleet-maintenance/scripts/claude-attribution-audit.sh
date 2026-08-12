#!/bin/bash

set -euo pipefail

usage() {
  printf 'usage: %s [--repair]\n' "$0" >&2
}

repair=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repair)
      repair=true
      shift
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

node_bin=$(command -v node 2>/dev/null || true)
if [[ -z "$node_bin" ]]; then
  for candidate in /opt/homebrew/bin/node /usr/local/bin/node; do
    if [[ -x "$candidate" ]]; then
      node_bin="$candidate"
      break
    fi
  done
fi

if [[ -z "$node_bin" ]]; then
  printf 'claude-attribution: node is unavailable\n' >&2
  exit 1
fi

settings="$HOME/.claude/settings.json"

if [[ "$repair" == true ]]; then
  "$node_bin" - "$settings" <<'NODE'
const fs = require("node:fs");
const path = require("node:path");

const settingsPath = process.argv[2];
const settingsDirectory = path.dirname(settingsPath);
let settings = {};
let mode = 0o644;

if (fs.existsSync(settingsDirectory)) {
  const directoryStat = fs.lstatSync(settingsDirectory);
  if (!directoryStat.isDirectory() || directoryStat.isSymbolicLink()) {
    throw new Error(`refusing non-directory Claude configuration path: ${settingsDirectory}`);
  }
} else {
  fs.mkdirSync(settingsDirectory, { recursive: true, mode: 0o755 });
}

if (fs.existsSync(settingsPath)) {
  const settingsStat = fs.lstatSync(settingsPath);
  if (!settingsStat.isFile() || settingsStat.isSymbolicLink() || settingsStat.nlink !== 1) {
    throw new Error(`refusing non-regular or linked settings file: ${settingsPath}`);
  }
  mode = settingsStat.mode & 0o777;
  settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  if (!settings || typeof settings !== "object" || Array.isArray(settings)) {
    throw new Error(`settings root must be a JSON object: ${settingsPath}`);
  }
}

const existingAttribution = settings.attribution;
if (existingAttribution !== undefined && (
  !existingAttribution ||
  typeof existingAttribution !== "object" ||
  Array.isArray(existingAttribution)
)) {
  throw new Error(`attribution must be a JSON object: ${settingsPath}`);
}

settings.attribution = {
  ...(existingAttribution || {}),
  commit: "",
  pr: "",
  sessionUrl: false,
};

const temporaryPath = `${settingsPath}.tmp.${process.pid}`;
try {
  fs.writeFileSync(temporaryPath, `${JSON.stringify(settings, null, 2)}\n`, {
    encoding: "utf8",
    flag: "wx",
    mode,
  });
  fs.renameSync(temporaryPath, settingsPath);
} finally {
  try {
    fs.unlinkSync(temporaryPath);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
}
NODE
fi

"$node_bin" - "$settings" <<'NODE'
const fs = require("node:fs");

const settingsPath = process.argv[2];
if (!fs.existsSync(settingsPath)) {
  process.stderr.write(`claude-attribution: drift file=${settingsPath} state=missing\n`);
  process.exit(1);
}

let settings;
try {
  settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
} catch {
  process.stderr.write(`claude-attribution: drift file=${settingsPath} state=invalid-json\n`);
  process.exit(1);
}

const attribution = settings?.attribution;
const commit = attribution?.commit === "" ? "disabled" : "enabled";
const pr = attribution?.pr === "" ? "disabled" : "enabled";
const sessionUrl = attribution?.sessionUrl === false ? "disabled" : "enabled";
if (commit !== "disabled" || pr !== "disabled" || sessionUrl !== "disabled") {
  process.stderr.write(
    `claude-attribution: drift file=${settingsPath} commit=${commit} pr=${pr} session_url=${sessionUrl}\n`,
  );
  process.exit(1);
}

process.stdout.write(
  `claude-attribution: current file=${settingsPath} commit=${commit} pr=${pr} session_url=${sessionUrl}\n`,
);
NODE

"$node_bin" - "$HOME/Projects" <<'NODE'
const fs = require("node:fs");
const path = require("node:path");

const projectsRoot = process.argv[2];
const managedRoot = "/Library/Application Support/ClaudeCode";
const managedFiles = [];
const projectFiles = [];

const managedBase = path.join(managedRoot, "managed-settings.json");
if (fs.existsSync(managedBase)) managedFiles.push(managedBase);
const managedDropIns = path.join(managedRoot, "managed-settings.d");
if (fs.existsSync(managedDropIns)) {
  for (const name of fs.readdirSync(managedDropIns).sort()) {
    if (!name.startsWith(".") && name.endsWith(".json")) {
      managedFiles.push(path.join(managedDropIns, name));
    }
  }
}

function collectProjectSettings(directory, depth) {
  if (depth < 0 || !fs.existsSync(directory)) return;
  let entries;
  try {
    entries = fs.readdirSync(directory, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (!entry.isDirectory() || entry.isSymbolicLink()) continue;
    const candidate = path.join(directory, entry.name);
    if (entry.name === ".claude") {
      for (const settingsName of ["settings.json", "settings.local.json"]) {
        const settingsPath = path.join(candidate, settingsName);
        if (fs.existsSync(settingsPath)) projectFiles.push(settingsPath);
      }
      continue;
    }
    if (entry.name === ".git" || entry.name === "node_modules") continue;
    collectProjectSettings(candidate, depth - 1);
  }
}

// Fleet repositories live directly in Projects or in one grouping directory such as Projects/oss.
collectProjectSettings(projectsRoot, 2);

let conflicts = 0;
for (const settingsPath of [...managedFiles, ...projectFiles]) {
  let settings;
  try {
    settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  } catch {
    continue;
  }
  const attribution = settings?.attribution;
  if (!attribution || typeof attribution !== "object" || Array.isArray(attribution)) continue;
  const conflict =
    (Object.hasOwn(attribution, "commit") && attribution.commit !== "") ||
    (Object.hasOwn(attribution, "pr") && attribution.pr !== "") ||
    (Object.hasOwn(attribution, "sessionUrl") && attribution.sessionUrl !== false);
  if (conflict) {
    process.stderr.write(`claude-attribution: conflicting override file=${settingsPath}\n`);
    conflicts += 1;
  }
}

if (conflicts > 0) process.exit(1);
process.stdout.write(
  `claude-attribution-overrides: current managed=${managedFiles.length} project=${projectFiles.length}\n`,
);
NODE
