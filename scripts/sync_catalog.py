#!/usr/bin/env python3
"""Sync installed skills into this archive and rebuild its catalog."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


IGNORED_NAMES = {".git", "__pycache__", ".DS_Store"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    return parser.parse_args()


def ignore_entries(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES}


def frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    lines = parts[1].splitlines()
    prefix = f"{key}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = line[len(prefix) :].strip()
        if value in {"", ">", ">-", "|", "|-"}:
            continuation: list[str] = []
            for next_line in lines[index + 1 :]:
                if next_line and not next_line[0].isspace():
                    break
                stripped = next_line.strip()
                if stripped:
                    continuation.append(stripped)
            return " ".join(continuation) or None
        return value.strip("\"'") or None
    return None


def body_summary(text: str) -> str | None:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]

    summary: list[str] = []
    in_code_fence = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        if not line:
            if summary:
                break
            continue
        if line.startswith(("#", "<!--", "![", "---")):
            continue
        line = re.sub(r"^>\s*", "", line)
        line = re.sub(r"^[*_]+|[*_]+$", "", line).strip()
        if line:
            summary.append(line)
    return " ".join(summary) or None


def sanitize_description(value: str) -> str:
    value = value.split("'' metadata:", 1)[0]
    value = value.replace("''''", "'").replace("''", "'")
    return value.replace("—", "-").replace("–", "-").strip(" '\"")


def clean_cell(value: str) -> str:
    compact = re.sub(r"\s+", " ", sanitize_description(value)).strip()
    return compact.replace("|", r"\|")


def github_url(source: str, source_url: str | None) -> str | None:
    if source_url and "github.com" in source_url:
        return source_url.removesuffix(".git")
    if re.fullmatch(r"[^/]+/[^/]+", source):
        return f"https://github.com/{source}"
    return None


def load_provenance(lock_path: Path) -> dict[str, dict[str, object]]:
    if not lock_path.is_file():
        return {}
    payload = json.loads(lock_path.read_text(encoding="utf-8"))
    skills = payload.get("skills", {})
    return skills if isinstance(skills, dict) else {}


def sync_skills(source: Path, destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    for entry in sorted(source.iterdir(), key=lambda item: item.name.casefold()):
        if not entry.is_dir() or not any(entry.rglob("SKILL.md")):
            continue
        shutil.copytree(
            entry,
            destination / entry.name,
            dirs_exist_ok=True,
            symlinks=False,
            ignore=ignore_entries,
        )
        copied += 1
    return copied


def discover_skill_dirs(root: Path) -> list[Path]:
    discovered: list[Path] = []
    for entry in sorted(root.iterdir(), key=lambda item: item.name.casefold()):
        if not entry.is_dir():
            continue
        if (entry / "SKILL.md").is_file():
            discovered.append(entry)
            continue
        candidates = sorted(
            (path.parent for path in entry.rglob("SKILL.md")),
            key=lambda item: str(item.relative_to(root)).casefold(),
        )
        selected: list[Path] = []
        for candidate in candidates:
            if any(parent in selected for parent in candidate.parents):
                continue
            selected.append(candidate)
        discovered.extend(selected)
    return discovered


def render_catalog(destination: Path, provenance: dict[str, dict[str, object]]) -> str:
    rows: list[str] = []
    for entry in discover_skill_dirs(destination):
        skill_file = entry / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        description = (
            frontmatter_value(text, "description")
            or body_summary(text)
            or "No description provided. Read SKILL.md."
        )
        metadata = provenance.get(entry.name, {})
        source = str(metadata.get("source") or "Archive copy")
        source_url = github_url(source, metadata.get("sourceUrl") if isinstance(metadata.get("sourceUrl"), str) else None)
        source_cell = f"[{source}]({source_url})" if source_url else source
        relative_path = entry.relative_to(destination).as_posix()
        rows.append(
            f"| [`{entry.name}`](skills/{relative_path}/) | {clean_cell(description)} | {source_cell} |"
        )

    header = (
        "# Skill catalog\n\n"
        f"{len(rows)} skills. Descriptions come from each skill's `SKILL.md`. "
        "Source links come from the installed-skill lock when available. "
        "See [INSTALL.md](INSTALL.md) for installation and update commands.\n\n"
        "| Skill | What it does | Source |\n"
        "|---|---|---|\n"
    )
    return header + "\n".join(rows) + "\n"


def main() -> int:
    args = parse_args()
    copied = sync_skills(args.source.expanduser(), args.destination)
    provenance = load_provenance(args.lock.expanduser())
    catalog = render_catalog(args.destination, provenance)
    args.catalog.write_text(catalog, encoding="utf-8")
    print(f"Synced {copied} installed skills; cataloged {catalog.count('| [`')} archive skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
