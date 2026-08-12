#!/usr/bin/env python3
"""Embed referenced source files into a readout's code-pane snippet blob.

Scans an HTML readout for GitHub blob links, extracts each referenced file at its
pinned commit from a local git checkout (git show <commit>:<path>), and injects a
<script type="application/json" data-code-snippets> blob that the bundled code
pane reads. Files are embedded whole; anything larger than a couple of KB is
gzip+base64'd ("gz"), which the pane inflates in the browser via
DecompressionStream. This makes the pane work offline and for private repos with
zero reader setup.

Usage:
  python3 embed_snippets.py <doc.html> --repo <checkout-path> [--repo <path> ...]

Each --repo must be a git checkout; its origin remote determines which org/repo
links it can satisfy. Re-running replaces any existing snippet blob.
"""
import argparse
import base64
import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

BLOB_RE = re.compile(r'https://github\.com/([^/"\s<>]+)/([^/"\s<>]+)/blob/([^/"\s<>]+)/([^"#\s<>?]+)')
# Requires "{" right after the tag so the mention of this tag inside the code-pane
# asset's header comment can never match (a real blob always starts with JSON).
SNIPPET_BLOCK_RE = re.compile(
    r'<script type="application/json" data-code-snippets>\s*\{.*?</script>\n?', re.S
)
GZ_THRESHOLD = 2048


def repo_slug(checkout: Path):
    """(org, repo) from the checkout's origin remote, or None."""
    r = subprocess.run(
        ["git", "-C", str(checkout), "remote", "get-url", "origin"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/(.+?)(?:\.git)?/?$", r.stdout.strip())
    return (m.group(1), m.group(2)) if m else None


def file_at(checkout: Path, commit: str, path: str):
    """File contents at the pinned commit, falling back to HEAD. -> (text, ref) or None."""
    for ref in (commit, "HEAD"):
        r = subprocess.run(
            ["git", "-C", str(checkout), "show", f"{ref}:{path}"],
            capture_output=True,
        )
        if r.returncode == 0:
            try:
                return r.stdout.decode("utf-8"), ref
            except UnicodeDecodeError:
                return None  # binary file; nothing sensible to embed
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc", type=Path, help="readout HTML file to modify in place")
    ap.add_argument("--repo", action="append", type=Path, default=[], required=True,
                    help="git checkout that can satisfy links (repeatable)")
    args = ap.parse_args()

    html = args.doc.read_text()
    refs = {m for m in BLOB_RE.findall(html)}
    if not refs:
        print("No GitHub blob links found; nothing to embed.")
        return 0

    slugs = {}
    for checkout in args.repo:
        slug = repo_slug(checkout)
        if slug is None:
            print(f"warning: {checkout} has no GitHub origin remote; skipping", file=sys.stderr)
            continue
        slugs.setdefault(slug, checkout)

    snippets, missing, from_head = {}, [], []
    for org, repo, commit, path in sorted(refs):
        label = f"{org}/{repo}@{commit[:10]}:{path}"
        checkout = slugs.get((org, repo))
        if checkout is None:
            missing.append(f"{label} (no --repo checkout for {org}/{repo})")
            continue
        got = file_at(checkout, commit, path)
        if got is None:
            missing.append(f"{label} (not found in {checkout}, or binary)")
            continue
        text, ref_used = got
        if ref_used != commit:
            from_head.append(label)
        entry = {"start": 1, "full": True}
        raw = text.encode("utf-8")
        if len(raw) > GZ_THRESHOLD:
            entry["gz"] = base64.b64encode(gzip.compress(raw, 9)).decode("ascii")
        else:
            entry["text"] = text
        snippets[f"{org}/{repo}@{commit}:{path}"] = entry

    if not snippets:
        print("Nothing could be embedded:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1

    # "</" must not appear literally inside a <script> block; "<\/" is the same string in JSON.
    payload = json.dumps(snippets, ensure_ascii=False).replace("</", "<\\/")
    block = f'<script type="application/json" data-code-snippets>\n{payload}\n</script>\n'

    if SNIPPET_BLOCK_RE.search(html):
        html = SNIPPET_BLOCK_RE.sub(lambda _: block, html, count=1)
        where = "replaced existing blob"
    elif "<style data-code-pane>" in html:
        html = html.replace("<style data-code-pane>", block + "<style data-code-pane>", 1)
        where = "inserted before code-pane asset"
    elif "</body>" in html:
        html = html.replace("</body>", block + "</body>", 1)
        where = "inserted before </body>"
    else:
        html = html + "\n" + block
        where = "appended (no </body> found)"

    args.doc.write_text(html)

    print(f"Embedded {len(snippets)} file(s) into {args.doc} ({where}); blob is {len(payload):,} bytes.")
    if from_head:
        print("warning: pinned commit not found locally; embedded from HEAD instead (content may drift from links):", file=sys.stderr)
        for m in from_head:
            print(f"  - {m}", file=sys.stderr)
    if missing:
        print("warning: could not embed (pane will fall back to fetch/token):", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
