# /// script
# requires-python = ">=3.11"
# dependencies = [
# ]
# ///
"""Render a Claude Code session .jsonl transcript into readable Markdown.

    uv run "$SKILL_DIR"/scripts/export_session.py <session.jsonl> <out.md>

Best-effort: walks the transcript, emitting user prompts, assistant text,
tool calls (name + compact input), and tool results (truncated).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

MAXLEN = 1600  # truncate long tool inputs/outputs

def trunc(s: str, n: int = MAXLEN) -> str:
    s = s if isinstance(s, str) else json.dumps(s, default=str)
    s = s.strip()
    return s if len(s) <= n else s[:n] + f"\n…[truncated {len(s)-n} chars]"

def text_of(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                parts.append(str(b)); continue
            t = b.get("type")
            if t == "text":
                parts.append(b.get("text", ""))
            elif t == "thinking":
                continue  # skip private reasoning
            elif t == "tool_use":
                parts.append(f"\n**🔧 tool: `{b.get('name')}`**\n```json\n{trunc(b.get('input', {}))}\n```")
            elif t == "tool_result":
                parts.append(f"\n**↩ result:**\n```\n{trunc(b.get('content'))}\n```")
    return "\n".join(p for p in parts if p)

def main(argv):
    src, out = Path(argv[0]), Path(argv[1])
    lines = src.read_text().splitlines()
    md = ["# Session transcript", f"\n_Source: `{src.name}`  ·  {len(lines)} events_\n"]
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        role = ev.get("type") or ev.get("role")
        msg = ev.get("message") or {}
        content = msg.get("content", ev.get("content"))
        if role == "user":
            body = text_of(content)
            if body.strip():
                md.append(f"\n---\n\n## 👤 User\n\n{body}")
        elif role == "assistant":
            body = text_of(content)
            if body.strip():
                md.append(f"\n### 🤖 Assistant\n\n{body}")
    out.write_text("\n".join(md))
    print(f"wrote {out} ({out.stat().st_size} bytes)")

if __name__ == "__main__":
    main(sys.argv[1:])
