#!/bin/bash
set -euo pipefail

usage() {
  printf 'usage: %s [--repair]\n' "${0##*/}" >&2
  exit 2
}

repair=no
case ${1-} in
  "") ;;
  --repair) repair=yes ;;
  *) usage ;;
esac
[[ $# -le 1 ]] || usage

host_name=$(hostname)
developer_dir=$(xcode-select -p 2>/dev/null || true)
simctl=""
xcode_app_count=0
if [[ -n $developer_dir ]]; then
  simctl=$(DEVELOPER_DIR="$developer_dir" xcrun --find simctl 2>/dev/null || true)
fi

if [[ -z $simctl ]]; then
  shopt -s nullglob
  for app in /Applications/Xcode*.app "$HOME"/Applications/Xcode*.app; do
    xcode_app_count=$((xcode_app_count + 1))
    candidate_developer="$app/Contents/Developer"
    candidate_simctl=$(DEVELOPER_DIR="$candidate_developer" xcrun --find simctl 2>/dev/null || true)
    if [[ -n $candidate_simctl ]]; then
      developer_dir=$candidate_developer
      simctl=$candidate_simctl
      break
    fi
  done
fi

if [[ -z $simctl ]]; then
  printf 'host\t%s\n' "$host_name"
  printf 'simctl\tabsent\n'
  if [[ $xcode_app_count -gt 0 ]]; then
    printf 'status\tblocked-xcode-not-ready\n'
    exit 1
  fi
  printf 'status\tnot-applicable\n'
  exit 0
fi

work_dir=$(mktemp -d "${TMPDIR:-/tmp}/xcode-simulator-hygiene.XXXXXX")
cleanup() { rm -rf "$work_dir"; }
trap cleanup EXIT

capture_runtime_candidates() {
  local kind=$1 output=$2 command_status
  set +e
  simctl_run runtime delete "--$kind" --dry-run >"$output.raw" 2>&1
  command_status=$?
  set -e
  if [[ $command_status -ne 0 ]] && ! grep -q 'No matching images found to delete' "$output.raw"; then
    cat "$output.raw" >&2
    return "$command_status"
  fi
  sed -e '/^[[:space:]]*$/d' -e '/No matching images found to delete/d' "$output.raw" >"$output"
}

simctl_run() {
  DEVELOPER_DIR="$developer_dir" xcrun simctl "$@"
}

delete_runtime_candidates() {
  local kind=$1 command_status
  set +e
  simctl_run runtime delete "--$kind" >"$work_dir/delete-$kind" 2>&1
  command_status=$?
  set -e
  if [[ $command_status -ne 0 ]] && ! grep -q 'No matching images found to delete' "$work_dir/delete-$kind"; then
    cat "$work_dir/delete-$kind" >&2
    return "$command_status"
  fi
}

count_device_rows() {
  awk '/\([0-9A-Fa-f-][0-9A-Fa-f-]*\)/ { count += 1 } END { print count + 0 }' "$1"
}

audit() {
  capture_runtime_candidates outdated "$work_dir/outdated"
  capture_runtime_candidates unusable "$work_dir/unusable"
  simctl_run list devices unavailable >"$work_dir/unavailable-devices"
  simctl_run list devices booted >"$work_dir/booted-devices"

  outdated_count=$(wc -l <"$work_dir/outdated" | tr -d ' ')
  unusable_count=$(wc -l <"$work_dir/unusable" | tr -d ' ')
  unavailable_device_count=$(count_device_rows "$work_dir/unavailable-devices")
  booted_device_count=$(count_device_rows "$work_dir/booted-devices")
}

print_audit() {
  local result=$1
  printf 'host\t%s\n' "$host_name"
  printf 'simctl\t%s\n' "$simctl"
  printf 'status\t%s\n' "$result"
  printf 'outdated_runtime_candidates\t%s\n' "$outdated_count"
  printf 'unusable_runtime_candidates\t%s\n' "$unusable_count"
  printf 'unavailable_devices\t%s\n' "$unavailable_device_count"
  printf 'booted_devices\t%s\n' "$booted_device_count"
  if [[ $outdated_count -gt 0 ]]; then
    sed 's/^/outdated_runtime\t/' "$work_dir/outdated"
  fi
  if [[ $unusable_count -gt 0 ]]; then
    sed 's/^/unusable_runtime\t/' "$work_dir/unusable"
  fi
}

audit
if [[ $outdated_count -eq 0 && $unusable_count -eq 0 && $unavailable_device_count -eq 0 ]]; then
  print_audit current
  exit 0
fi

if [[ $repair == no ]]; then
  print_audit drift
  exit 1
fi

if [[ $booted_device_count -gt 0 ]]; then
  print_audit blocked-booted-devices
  printf 'refusing repair while simulator devices are booted\n' >&2
  exit 3
fi

if [[ $outdated_count -gt 0 ]]; then
  delete_runtime_candidates outdated
fi
if [[ $unusable_count -gt 0 ]]; then
  delete_runtime_candidates unusable
fi
simctl_run delete unavailable

audit
if [[ $outdated_count -ne 0 || $unusable_count -ne 0 || $unavailable_device_count -ne 0 ]]; then
  print_audit repair-incomplete
  exit 1
fi
print_audit repaired
