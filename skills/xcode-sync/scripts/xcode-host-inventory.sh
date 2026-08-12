#!/bin/bash
set -euo pipefail

shopt -s nullglob

host_name=$(hostname)
macos_version=$(sw_vers -productVersion)
architecture=$(uname -m)
hardware_uuid=$(
  ioreg -rd1 -c IOPlatformExpertDevice |
    awk -F'"' '/IOPlatformUUID/ { print $4; exit }'
)
selected_developer=$(xcode-select -p 2>/dev/null || true)
selected_app=${selected_developer%/Contents/Developer}

printf 'host\t%s\t%s\t%s\t%s\t%s\n' \
  "$host_name" "$hardware_uuid" "$macos_version" "$architecture" "$selected_app"

apps=(/Applications/Xcode*.app "$HOME"/Applications/Xcode*.app)
for app in "${apps[@]}"; do
  [[ -d "$app" ]] || continue
  version=$(plutil -extract CFBundleShortVersionString raw -o - "$app/Contents/Info.plist" 2>/dev/null || printf '?')
  build=$(plutil -extract ProductBuildVersion raw -o - "$app/Contents/version.plist" 2>/dev/null || printf '?')
  minimum=$(plutil -extract LSMinimumSystemVersion raw -o - "$app/Contents/Info.plist" 2>/dev/null || printf '?')
  selected=no
  [[ "$app" == "$selected_app" ]] && selected=yes
  printf 'xcode\t%s\t%s\t%s\t%s\t%s\n' \
    "$app" "$version" "$build" "$minimum" "$selected"
done
