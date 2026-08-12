#!/usr/bin/env python3
"""Regenerate the readouts index page.

Scans a readouts directory for .html files (excluding index.html), pulls each
document's <title>, <meta name="description">, and date (filename YYYY-MM-DD
prefix, else mtime), and writes a styled index.html listing every readout
newest-first. The index is fully regenerated on every run, so it is always
safe to re-run and never drifts from the directory contents.

Usage:
  python3 update_index.py [readouts_dir]     (default: ~/.readouts)
"""
import html
import re
import sys
from datetime import datetime
from pathlib import Path

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="(.*?)"', re.S | re.I)
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Readouts</title>
<style>
  :root { --bg: #faf8f4; --fg: #262220; --muted: #857c6e; --hairline: #e3ddd1; --accent: #31567d; }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #1e1c19; --fg: #e8e4dc; --muted: #948b7c; --hairline: #383530; --accent: #8caec9; }
  }
  body {
    margin: 0; background: var(--bg); color: var(--fg);
    font-family: Charter, 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
    line-height: 1.6;
  }
  main { max-width: 44rem; margin: 0 auto; padding: 3rem 1.25rem 4rem; }
  h1 { font-size: 1.6rem; margin: 0 0 0.3rem; }
  .sub { color: var(--muted); font-size: 0.9rem; margin: 0 0 2rem; }
  ol { list-style: none; margin: 0; padding: 0; }
  li { padding: 1rem 0; border-top: 1px solid var(--hairline); }
  li:last-child { border-bottom: 1px solid var(--hairline); }
  .date {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.72rem; color: var(--muted); letter-spacing: 0.04em;
  }
  a.title { color: var(--fg); font-size: 1.05rem; font-weight: 600; text-decoration: none; display: block; margin: 0.15rem 0; }
  a.title:hover { color: var(--accent); }
  p.desc { margin: 0.1rem 0 0; color: var(--muted); font-size: 0.9rem; }
  p.empty { color: var(--muted); }
  footer { margin-top: 2.5rem; color: var(--muted); font-size: 0.78rem; }
</style>
</head>
<body>
<main>
<h1>Readouts</h1>
<p class="sub">__COUNT__ document__PLURAL__ &middot; newest first</p>
<ol>
__ITEMS__
</ol>
<footer>Index regenerated __UPDATED__ by the readout skill. Run <code>update_index.py</code> to refresh.</footer>
</main>
</body>
</html>
"""

ITEM = """  <li>
    <span class="date">__DATE__</span>
    <a class="title" href="__FILE__">__TITLE__</a>
__DESC__  </li>"""


def entry(p: Path):
    src = p.read_text(errors="replace")
    m = TITLE_RE.search(src)
    title = html.unescape(m.group(1).strip()) if m else p.stem
    m = DESC_RE.search(src)
    desc = html.unescape(m.group(1).strip()) if m else ""
    m = DATE_RE.match(p.name)
    date = m.group(1) if m else datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    return {"file": p.name, "title": title, "desc": desc, "date": date, "mtime": p.stat().st_mtime}


def main() -> int:
    d = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / ".readouts"
    d.mkdir(parents=True, exist_ok=True)
    docs = [entry(p) for p in sorted(d.glob("*.html")) if p.name != "index.html"]
    docs.sort(key=lambda e: (e["date"], e["mtime"]), reverse=True)

    items = []
    for e in docs:
        desc_html = f'    <p class="desc">{html.escape(e["desc"])}</p>\n' if e["desc"] else ""
        items.append(
            ITEM.replace("__DATE__", e["date"])
                .replace("__FILE__", html.escape(e["file"], quote=True))
                .replace("__TITLE__", html.escape(e["title"]))
                .replace("__DESC__", desc_html)
        )
    body = "\n".join(items) if items else '  <p class="empty">No readouts yet.</p>'

    page = (PAGE.replace("__COUNT__", str(len(docs)))
                .replace("__PLURAL__", "" if len(docs) == 1 else "s")
                .replace("__ITEMS__", body)
                .replace("__UPDATED__", datetime.now().strftime("%Y-%m-%d %H:%M")))
    (d / "index.html").write_text(page)
    print(f"Indexed {len(docs)} readout(s) -> {d / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
