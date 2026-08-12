---
name: openrouter
description: Browse and run any of the ~350 models served by the local cli-proxy-api (all OpenRouter models plus Codex). Use when the user types /openrouter, asks which models are available, wants to switch to a specific model, or wants to run a task on a non-Claude model to save quota.
---

# openrouter

Every OpenRouter model plus the Codex models are served by `cli-proxy-api` on
`http://127.0.0.1:8317`. This skill lists them and explains how to run one.

## Important: a model cannot be swapped inside a running session

The model for the current conversation is fixed. To use a different one, the user
starts a new session against it. So this skill's job is to **help them choose**,
then hand them the exact command.

## List what is available

```sh
openrouter --list                     # all model names
openrouter --list | grep -i gemini    # filter
openrouter --refresh                  # re-fetch after OpenRouter adds models
```

## Launch a model

```sh
openrouter                     # fuzzy picker over every model
openrouter deepseek            # jump straight there (picker if ambiguous)
openrouter gemini-3.6-flash    # exact name
```

The picker uses fzf: type to filter, Enter to launch, Esc to cancel.

There is also `aim <model>` in the shell, which does the same thing without a
picker.

## When to suggest a non-Claude model

Check remaining quota first:

```sh
quota-axi
```

Reach for another model when the Claude weekly window is low and the task does
not need Claude specifically. Good substitutes by job:

| Job | Try |
|---|---|
| Bulk edits, mechanical refactors | `deepseek-chat`, `qwen` variants |
| Long-context reading | `gemini-3.6-flash`, `gemini-pro` |
| Reasoning-heavy analysis | `deepseek-r1` |
| Cheap throwaway questions | any `:free` variant |

Free variants are suffixed `:free` in the model id and cost nothing, at the price
of rate limits.

## Procedure when the user invokes this

1. Run `openrouter --list` and, unless they asked for everything, show a relevant
   filtered subset rather than all 349 lines.
2. If they named a task, recommend two or three fitting models with one line each
   on why.
3. Give them the exact command to run, and state plainly that it starts a new
   session rather than switching this one.
4. If they want the work done now inside this session instead, offer to do it
   here on the current model.

## Troubleshooting

`openrouter: could not reach the proxy` - the service is down:

```sh
brew services restart cliproxyapi
```

A model that 404s has probably been renamed or retired by OpenRouter. Run
`openrouter --refresh`; if it is genuinely gone, the proxy config at
`/opt/homebrew/etc/cliproxyapi.conf` needs regenerating from the live list.
