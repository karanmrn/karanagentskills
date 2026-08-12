# mcporter Chrome Config

Use when Chrome DevTools MCP attaches to a blank/isolated browser, cannot see the user's real tabs, or errors around `DevToolsActivePort`.

## Expected Setup

Home config owns the default:

```bash
mcporter config get chrome-devtools --json
```

Check the `source.path` in that output. If it points at a repo `config/mcporter.json`, project config is overriding home config. Either run from a neutral cwd such as `$HOME` for browser automation, or update the project override with `--scope project` too.

Expected entry:

```json
{
  "command": "npx",
  "args": [
    "-y",
    "chrome-devtools-mcp",
    "--auto-connect",
    "--userDataDir",
    "/Users/steipete/Library/Application Support/Google/Chrome"
  ]
}
```

`chrome-devtools` means reattach to existing Chrome. `chrome-isolated` is the explicit fresh-session escape hatch.

## Verify

```bash
mcporter call chrome-devtools.list_pages --args '{}' --output text
```

Pass: output lists the user's visible tabs.

Fail: output shows only `about:blank`, a single empty tab, or a page set that does not match Chrome.

## Fix Default Config

```bash
mcporter config add chrome-isolated --scope home --command npx --arg -y --arg chrome-devtools-mcp --description "Chrome DevTools MCP - isolated browser for explicit fresh-session tests"
mcporter config add chrome-devtools --scope home --command npx --arg -y --arg chrome-devtools-mcp --arg --auto-connect --arg --userDataDir --arg "$HOME/Library/Application Support/Google/Chrome" --description "Chrome DevTools MCP - reattach existing Chrome profile"
```

If `mcporter config get chrome-devtools --json` reports a project `source.path`, repair that project override too:

```bash
mcporter config add chrome-devtools --scope project --command npx --arg -y --arg chrome-devtools-mcp --arg --auto-connect --arg --userDataDir --arg "$HOME/Library/Application Support/Google/Chrome" --description "Chrome DevTools MCP - reattach existing Chrome profile"
```

Then verify again:

```bash
mcporter call chrome-devtools.list_pages --args '{}' --output text
```

## Recovery

If `DevToolsActivePort` or connection startup fails:

```bash
mcporter daemon restart
mcporter call chrome-devtools.list_pages --args '{}' --output text
```

Retry once. If still broken, ask the user to restart Chrome or the DevTools bridge. Do not switch to AppleScript, Playwright, Puppeteer, or `chrome-isolated` unless the user explicitly asks for a fresh browser.

## Source Notes

mcporter loads config layers from:

- explicit `--config` or `$MCPORTER_CONFIG`
- first existing home config: `~/.mcporter/mcporter.json` or `.jsonc`
- project `config/mcporter.json`

Avoid `/tmp` config files for Chrome. They bypass normal config discovery and make agents copy long commands that are easy to misuse.
