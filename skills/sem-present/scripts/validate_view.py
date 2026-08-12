#!/usr/bin/env python3
"""Validate a Sem run view bundle without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
VERSION_RE = re.compile(r"^1\.[0-9]+$")
RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-][0-9]{2}:[0-9]{2})$"
)
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
EXTENSION_RE = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)+$")

STATUSES = {
    "unknown", "pending", "ready", "running", "succeeded", "failed",
    "blocked", "partial",
}
NONTERMINAL_STATUSES = {"unknown", "pending", "ready", "running"}
TERMINAL_STATUSES = {"succeeded", "failed", "blocked", "partial"}
ARTIFACT_ROLES = {
    "request", "compiler-prompt", "program", "compile-notes",
    "interpretation", "run-log", "input", "application-prompt",
    "application-result", "application-status", "attempt",
    "finalizer-prompt", "final", "other",
}
NODE_TYPES = {"source", "stage", "application", "result", "group", "event", "note"}
EMPHASES = {"primary", "normal", "context", "hidden"}
PANEL_ROLES = {"primary", "result", "prompt", "status", "source", "explanation", "attempt", "other"}
RENDER_MODES = {"markdown", "code", "plain-text", "metadata", "download"}
EDGE_TYPES = {"value", "control", "return", "contains", "retry", "provenance"}
GROUP_TYPES = {"fan-out", "map", "iteration", "choice", "retry", "phase", "other"}
OPERATOR_KINDS = {"standard-library", "local", "semantic-judgment"}
WARNING_SEVERITIES = {"info", "warning", "error"}


def _exception_text(exc: BaseException) -> str:
    return getattr(exc, "strerror", None) or str(exc)


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard numeric constant {value!r}")


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate object key {key!r}")
        result[key] = value
    return result


class Validator:
    def __init__(self, run_root: Path, manifest_path: Path, canonical: bool) -> None:
        self.run_root = run_root
        self.root_real = run_root.resolve()
        self.manifest_path = manifest_path
        self.canonical = canonical
        self.errors: list[str] = []
        self.manifest: dict[str, Any] | None = None

    def error(self, location: str, message: str) -> None:
        self.errors.append(f"{location}: {message}")

    def validate(self) -> list[str]:
        if not self.run_root.exists():
            self.error("run", "run root does not exist")
            return self.errors
        if not self.run_root.is_dir():
            self.error("run", "run root is not a directory")
            return self.errors
        if not self._inside_root(self.root_real):
            self.error("run", "could not resolve run root")
            return self.errors
        if not self._safe_manifest_target():
            return self.errors

        try:
            with self.manifest_path.open("r", encoding="utf-8") as handle:
                value = json.load(
                    handle,
                    parse_constant=_reject_json_constant,
                    object_pairs_hook=_reject_duplicate_json_keys,
                )
        except json.JSONDecodeError as exc:
            self.error("manifest", f"invalid JSON at line {exc.lineno}, column {exc.colno}")
            return self.errors
        except (ValueError, RecursionError) as exc:
            self.error("manifest", f"invalid JSON: {_exception_text(exc)}")
            return self.errors
        except (OSError, RuntimeError) as exc:
            self.error("manifest", f"cannot read manifest: {_exception_text(exc)}")
            return self.errors

        if not isinstance(value, dict):
            self.error("manifest", "must be an object")
            return self.errors
        self.manifest = value
        self._validate_structure()
        self._validate_cross_references_and_filesystem()
        if self.canonical:
            self._validate_notes()
        return self.errors

    def _safe_manifest_target(self) -> bool:
        try:
            target = self.manifest_path.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            self.error("manifest", f"manifest does not resolve to an existing file: {_exception_text(exc)}")
            return False
        if not self._inside_root(target):
            self.error("manifest", "manifest resolves outside the run root")
            return False
        if not target.is_file():
            self.error("manifest", "manifest is not a regular file")
            return False
        return True

    def _inside_root(self, target: Path) -> bool:
        try:
            target.relative_to(self.root_real)
            return True
        except ValueError:
            return False

    def _required(self, obj: dict[str, Any], keys: Iterable[str], location: str) -> None:
        for key in keys:
            if key not in obj:
                self.error(f"{location}.{key}", "required field is missing")

    def _object(self, value: Any, location: str) -> dict[str, Any] | None:
        if not isinstance(value, dict):
            self.error(location, "must be an object")
            return None
        return value

    def _array(self, value: Any, location: str) -> list[Any] | None:
        if not isinstance(value, list):
            self.error(location, "must be an array")
            return None
        return value

    def _string(self, value: Any, location: str, *, nonempty: bool = False) -> str | None:
        if not isinstance(value, str):
            self.error(location, "must be a string")
            return None
        if nonempty and not value:
            self.error(location, "must not be empty")
            return None
        return value

    def _boolean(self, value: Any, location: str) -> bool | None:
        if not isinstance(value, bool):
            self.error(location, "must be a boolean")
            return None
        return value

    def _integer(self, value: Any, location: str, minimum: int = 0) -> int | None:
        if isinstance(value, bool) or not isinstance(value, int):
            self.error(location, "must be an integer")
            return None
        if value < minimum:
            self.error(location, f"must be at least {minimum}")
            return None
        return value

    def _enum(self, value: Any, allowed: set[str], location: str) -> str | None:
        string = self._string(value, location)
        if string is not None and string not in allowed:
            self.error(location, f"unsupported value {string!r}")
            return None
        return string

    def _id(self, value: Any, location: str) -> str | None:
        string = self._string(value, location, nonempty=True)
        if string is None:
            return None
        if len(string) > 160 or not ID_RE.fullmatch(string):
            self.error(location, "must be a valid ID")
            return None
        return string

    def _id_list(self, value: Any, location: str) -> list[str] | None:
        items = self._array(value, location)
        if items is None:
            return None
        result: list[str] = []
        seen: set[str] = set()
        for index, item in enumerate(items):
            item_location = f"{location}[{index}]"
            identifier = self._id(item, item_location)
            if identifier is None:
                continue
            if identifier in seen:
                self.error(item_location, f"duplicate ID {identifier!r}")
            else:
                seen.add(identifier)
                result.append(identifier)
        return result

    def _unique_ids(self, records: list[Any] | None, location: str) -> None:
        if records is None:
            return
        seen: dict[str, int] = {}
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            identifier = record.get("id")
            if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
                continue
            if identifier in seen:
                self.error(f"{location}[{index}].id", f"duplicate ID {identifier!r}; first used at {location}[{seen[identifier]}].id")
            else:
                seen[identifier] = index

    def _validate_structure(self) -> None:
        assert self.manifest is not None
        manifest = self.manifest
        required = (
            "kind", "schemaVersion", "generatedAt", "run", "artifacts",
            "nodes", "edges", "groups", "presentation", "warnings", "extensions",
        )
        self._required(manifest, required, "manifest")

        if "kind" in manifest and manifest["kind"] != "sem-run-view":
            self.error("manifest.kind", "must equal 'sem-run-view'")
        if "schemaVersion" in manifest:
            version = self._string(manifest["schemaVersion"], "manifest.schemaVersion")
            if version is not None and not VERSION_RE.fullmatch(version):
                self.error("manifest.schemaVersion", "must be a supported version 1.x")
        if "generatedAt" in manifest:
            stamp = self._string(manifest["generatedAt"], "manifest.generatedAt")
            if stamp is not None:
                try:
                    if not RFC3339_RE.fullmatch(stamp):
                        raise ValueError
                    normalized = stamp[:-1] + "+00:00" if stamp[-1:] in {"Z", "z"} else stamp
                    parsed = datetime.fromisoformat(normalized)
                    if parsed.tzinfo is None:
                        raise ValueError
                except ValueError:
                    self.error("manifest.generatedAt", "must be an RFC 3339 date-time with a UTC offset")

        if "run" in manifest:
            self._validate_run(manifest["run"])
        artifacts = self._array(manifest.get("artifacts"), "manifest.artifacts") if "artifacts" in manifest else None
        nodes = self._array(manifest.get("nodes"), "manifest.nodes") if "nodes" in manifest else None
        edges = self._array(manifest.get("edges"), "manifest.edges") if "edges" in manifest else None
        groups = self._array(manifest.get("groups"), "manifest.groups") if "groups" in manifest else None
        warnings = self._array(manifest.get("warnings"), "manifest.warnings") if "warnings" in manifest else None

        if artifacts is not None:
            for index, artifact in enumerate(artifacts):
                self._validate_artifact(artifact, f"manifest.artifacts[{index}]")
        if nodes is not None:
            for index, node in enumerate(nodes):
                self._validate_node(node, f"manifest.nodes[{index}]")
        if edges is not None:
            for index, edge in enumerate(edges):
                self._validate_edge(edge, f"manifest.edges[{index}]")
        if groups is not None:
            for index, group in enumerate(groups):
                self._validate_group(group, f"manifest.groups[{index}]")
        if "presentation" in manifest:
            self._validate_presentation(manifest["presentation"])
        if warnings is not None:
            for index, warning in enumerate(warnings):
                self._validate_warning(warning, f"manifest.warnings[{index}]")
        if "extensions" in manifest:
            self._validate_extensions(manifest["extensions"])

        self._unique_ids(artifacts, "manifest.artifacts")
        self._unique_ids(nodes, "manifest.nodes")
        self._unique_ids(edges, "manifest.edges")
        self._unique_ids(groups, "manifest.groups")

    def _validate_run(self, value: Any) -> None:
        obj = self._object(value, "manifest.run")
        if obj is None:
            return
        self._required(obj, ("title", "status", "snapshot"), "manifest.run")
        if "title" in obj:
            self._string(obj["title"], "manifest.run.title", nonempty=True)
        status = (
            self._enum(obj["status"], STATUSES, "manifest.run.status")
            if "status" in obj else None
        )
        snapshot = (
            self._boolean(obj["snapshot"], "manifest.run.snapshot")
            if "snapshot" in obj else None
        )
        if status is not None and snapshot is not None:
            expected = NONTERMINAL_STATUSES if snapshot else TERMINAL_STATUSES
            if status not in expected:
                state = "non-terminal" if snapshot else "terminal"
                self.error("manifest.run", f"snapshot {snapshot!r} requires a {state} status")

    def _validate_artifact(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("id", "path", "mediaType", "role", "title"), location)
        if "id" in obj:
            self._id(obj["id"], f"{location}.id")
        if "path" in obj:
            self._string(obj["path"], f"{location}.path", nonempty=True)
        if "mediaType" in obj:
            self._string(obj["mediaType"], f"{location}.mediaType", nonempty=True)
        if "role" in obj:
            self._enum(obj["role"], ARTIFACT_ROLES, f"{location}.role")
        if "title" in obj:
            self._string(obj["title"], f"{location}.title", nonempty=True)
        if "ownerNodeId" in obj:
            self._id(obj["ownerNodeId"], f"{location}.ownerNodeId")
        if "description" in obj:
            self._string(obj["description"], f"{location}.description")

    def _validate_node(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("id", "type", "title", "emphasis", "panels"), location)
        if "id" in obj:
            self._id(obj["id"], f"{location}.id")
        node_type = self._enum(obj.get("type"), NODE_TYPES, f"{location}.type") if "type" in obj else None
        if "title" in obj:
            self._string(obj["title"], f"{location}.title", nonempty=True)
        for field in ("subtitle", "summary"):
            if field in obj:
                self._string(obj[field], f"{location}.{field}")
        if "status" in obj:
            self._enum(obj["status"], STATUSES, f"{location}.status")
        if "emphasis" in obj:
            self._enum(obj["emphasis"], EMPHASES, f"{location}.emphasis")
        if "ordinal" in obj:
            self._integer(obj["ordinal"], f"{location}.ordinal")
        if "groupIds" in obj:
            self._id_list(obj["groupIds"], f"{location}.groupIds")
        panels = self._array(obj.get("panels"), f"{location}.panels") if "panels" in obj else None
        if panels is not None:
            for index, panel in enumerate(panels):
                self._validate_panel(panel, f"{location}.panels[{index}]")
            self._unique_ids(panels, f"{location}.panels")
        if node_type == "application":
            if "application" not in obj:
                self.error(f"{location}.application", "required for an application node")
            if "status" not in obj:
                self.error(f"{location}.status", "required for an application node")
        if "application" in obj:
            self._validate_application(obj["application"], f"{location}.application")

    def _validate_application(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("directory",), location)
        if "directory" in obj:
            directory_location = f"{location}.directory"
            directory = self._string(obj["directory"], directory_location, nonempty=True)
            if directory is not None:
                relative = self._safe_relative_path(directory, directory_location)
                if (
                    relative is not None
                    and (
                        len(relative.parts) != 2
                        or relative.parts[0] != "applications"
                        or relative.parts[1].startswith(".")
                    )
                ):
                    self.error(directory_location, "must name exactly applications/<application-id>")
        if "operator" in obj:
            operator = self._object(obj["operator"], f"{location}.operator")
            if operator is not None:
                self._required(operator, ("kind",), f"{location}.operator")
                if "kind" in operator:
                    self._enum(operator["kind"], OPERATOR_KINDS, f"{location}.operator.kind")
                if "name" in operator:
                    self._string(operator["name"], f"{location}.operator.name", nonempty=True)

    def _validate_panel(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("id", "label", "artifactId", "role", "renderAs"), location)
        if "id" in obj:
            self._id(obj["id"], f"{location}.id")
        if "label" in obj:
            self._string(obj["label"], f"{location}.label", nonempty=True)
        if "artifactId" in obj:
            self._id(obj["artifactId"], f"{location}.artifactId")
        if "role" in obj:
            self._enum(obj["role"], PANEL_ROLES, f"{location}.role")
        if "renderAs" in obj:
            self._enum(obj["renderAs"], RENDER_MODES, f"{location}.renderAs")
        if "order" in obj:
            self._integer(obj["order"], f"{location}.order")
        if "defaultOpen" in obj:
            self._boolean(obj["defaultOpen"], f"{location}.defaultOpen")
        if "selector" in obj:
            self._validate_selector(obj["selector"], f"{location}.selector")

    def _validate_selector(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("kind",), location)
        kind = self._string(obj.get("kind"), f"{location}.kind") if "kind" in obj else None
        if kind is None:
            return
        if kind not in {"whole", "markdown-heading"}:
            self.error(f"{location}.kind", f"unsupported value {kind!r}")
            return
        if kind == "markdown-heading":
            if "heading" not in obj:
                self.error(f"{location}.heading", "required for markdown-heading")
            else:
                self._string(obj["heading"], f"{location}.heading", nonempty=True)
            if "occurrence" in obj:
                self._integer(obj["occurrence"], f"{location}.occurrence", minimum=1)

    def _validate_edge(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("id", "from", "to", "type"), location)
        for field in ("id", "from", "to"):
            if field in obj:
                self._id(obj[field], f"{location}.{field}")
        if "type" in obj:
            self._enum(obj["type"], EDGE_TYPES, f"{location}.type")
        if "label" in obj:
            self._string(obj["label"], f"{location}.label")
        if "subtype" in obj:
            self._string(obj["subtype"], f"{location}.subtype", nonempty=True)
        if "order" in obj:
            self._integer(obj["order"], f"{location}.order")

    def _validate_group(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("id", "title", "type", "memberNodeIds"), location)
        if "id" in obj:
            self._id(obj["id"], f"{location}.id")
        if "title" in obj:
            self._string(obj["title"], f"{location}.title", nonempty=True)
        if "type" in obj:
            self._enum(obj["type"], GROUP_TYPES, f"{location}.type")
        if "memberNodeIds" in obj:
            self._id_list(obj["memberNodeIds"], f"{location}.memberNodeIds")
        if "parentGroupId" in obj:
            self._id(obj["parentGroupId"], f"{location}.parentGroupId")
        if "summary" in obj:
            self._string(obj["summary"], f"{location}.summary")
        if "collapsedByDefault" in obj:
            self._boolean(obj["collapsedByDefault"], f"{location}.collapsedByDefault")

    def _validate_presentation(self, value: Any) -> None:
        location = "manifest.presentation"
        obj = self._object(value, location)
        if obj is None:
            return
        fields = ("entryNodeIds", "featuredNodeIds", "resultNodeIds")
        self._required(obj, fields, location)
        for field in fields:
            if field in obj:
                self._id_list(obj[field], f"{location}.{field}")

    def _validate_warning(self, value: Any, location: str) -> None:
        obj = self._object(value, location)
        if obj is None:
            return
        self._required(obj, ("message",), location)
        if "message" in obj:
            self._string(obj["message"], f"{location}.message", nonempty=True)
        if "code" in obj:
            self._string(obj["code"], f"{location}.code", nonempty=True)
        if "severity" in obj:
            self._enum(obj["severity"], WARNING_SEVERITIES, f"{location}.severity")
        for field in ("nodeIds", "artifactIds"):
            if field in obj:
                self._id_list(obj[field], f"{location}.{field}")

    def _validate_extensions(self, value: Any) -> None:
        obj = self._object(value, "manifest.extensions")
        if obj is None:
            return
        for key in obj:
            if not EXTENSION_RE.fullmatch(key):
                self.error(f"manifest.extensions[{key!r}]", "key must be a namespaced identifier")

    def _records(self, name: str) -> list[dict[str, Any]]:
        assert self.manifest is not None
        value = self.manifest.get(name)
        if not isinstance(value, list):
            return []
        # Preserve source-array positions so later cross-record diagnostics use
        # the same indexes as structural diagnostics after malformed entries.
        return [item if isinstance(item, dict) else {} for item in value]

    def _record_map(self, name: str) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for record in self._records(name):
            identifier = record.get("id")
            if isinstance(identifier, str) and identifier not in result:
                result[identifier] = record
        return result

    def _validate_cross_references_and_filesystem(self) -> None:
        assert self.manifest is not None
        artifacts = self._record_map("artifacts")
        nodes = self._record_map("nodes")
        groups = self._record_map("groups")

        artifact_records = self._records("artifacts")
        node_records = self._records("nodes")
        edge_records = self._records("edges")
        group_records = self._records("groups")
        warning_records = self._records("warnings")

        for index, artifact in enumerate(artifact_records):
            owner = artifact.get("ownerNodeId")
            if isinstance(owner, str) and owner not in nodes:
                self.error(f"manifest.artifacts[{index}].ownerNodeId", f"unknown node ID {owner!r}")

        memberships: dict[str, set[str]] = {}
        for index, group in enumerate(group_records):
            group_id = group.get("id")
            members = group.get("memberNodeIds")
            if isinstance(members, list):
                for member_index, member in enumerate(members):
                    if not isinstance(member, str):
                        continue
                    if member not in nodes:
                        self.error(f"manifest.groups[{index}].memberNodeIds[{member_index}]", f"unknown node ID {member!r}")
                    elif isinstance(group_id, str):
                        memberships.setdefault(member, set()).add(group_id)
            parent = group.get("parentGroupId")
            if isinstance(parent, str) and parent not in groups:
                self.error(f"manifest.groups[{index}].parentGroupId", f"unknown group ID {parent!r}")

        for index, node in enumerate(node_records):
            group_ids = node.get("groupIds")
            if isinstance(group_ids, list):
                valid = {group_id for group_id in group_ids if isinstance(group_id, str)}
                for group_index, group_id in enumerate(group_ids):
                    if isinstance(group_id, str) and group_id not in groups:
                        self.error(f"manifest.nodes[{index}].groupIds[{group_index}]", f"unknown group ID {group_id!r}")
                node_id = node.get("id")
                expected = memberships.get(node_id, set()) if isinstance(node_id, str) else set()
                if valid != expected:
                    self.error(f"manifest.nodes[{index}].groupIds", f"reverse membership does not match groups; expected {sorted(expected)!r}")
            panels = node.get("panels")
            if not isinstance(panels, list):
                continue
            for panel_index, panel in enumerate(panels):
                if not isinstance(panel, dict):
                    continue
                artifact_id = panel.get("artifactId")
                panel_location = f"manifest.nodes[{index}].panels[{panel_index}]"
                if isinstance(artifact_id, str) and artifact_id not in artifacts:
                    self.error(f"{panel_location}.artifactId", f"unknown artifact ID {artifact_id!r}")
                elif isinstance(artifact_id, str):
                    self._validate_result_panel(node, panel, artifacts[artifact_id], panel_location)

        for index, edge in enumerate(edge_records):
            for field in ("from", "to"):
                endpoint = edge.get(field)
                if isinstance(endpoint, str) and endpoint not in nodes:
                    self.error(f"manifest.edges[{index}].{field}", f"unknown node ID {endpoint!r}")

        presentation = self.manifest.get("presentation")
        if isinstance(presentation, dict):
            for field in ("entryNodeIds", "featuredNodeIds", "resultNodeIds"):
                identifiers = presentation.get(field)
                if isinstance(identifiers, list):
                    for index, identifier in enumerate(identifiers):
                        if isinstance(identifier, str) and identifier not in nodes:
                            self.error(f"manifest.presentation.{field}[{index}]", f"unknown node ID {identifier!r}")
            self._validate_presentation_results(presentation, nodes, artifacts)
        for index, warning in enumerate(warning_records):
            for field, known, noun in (("nodeIds", nodes, "node"), ("artifactIds", artifacts, "artifact")):
                identifiers = warning.get(field)
                if isinstance(identifiers, list):
                    for ref_index, identifier in enumerate(identifiers):
                        if isinstance(identifier, str) and identifier not in known:
                            self.error(f"manifest.warnings[{index}].{field}[{ref_index}]", f"unknown {noun} ID {identifier!r}")

        self._validate_group_cycles(group_records)
        artifact_paths = self._validate_artifact_paths(artifact_records)
        self._validate_inventory(artifact_paths)
        self._validate_applications(node_records, artifact_paths)

        run = self.manifest.get("run")
        result_ids = presentation.get("resultNodeIds") if isinstance(presentation, dict) else None
        if isinstance(run, dict) and run.get("status") == "succeeded" and isinstance(result_ids, list) and not result_ids:
            self.error("manifest.presentation.resultNodeIds", "a succeeded run must expose at least one result node")

    def _validate_result_panel(self, node: dict[str, Any], panel: dict[str, Any], artifact: dict[str, Any], location: str) -> None:
        path = artifact.get("path")
        role = artifact.get("role")
        if panel.get("role") != "result":
            return
        if role == "attempt" or (isinstance(path, str) and "/attempts/" in path):
            self.error(f"{location}.artifactId", "result panel must not reference a rejected attempt artifact")
            return
        parts = PurePosixPath(path).parts if isinstance(path, str) else ()
        canonical_application = (
            role == "application-result"
            and len(parts) == 3
            and parts[0] == "applications"
            and parts[2] == "result.md"
        )
        canonical_final = role == "final" and path == "final.md"
        if not canonical_application and not canonical_final:
            self.error(f"{location}.artifactId", "result panel must reference a canonical accepted result artifact")
            return
        application = node.get("application")
        if node.get("type") == "application" and isinstance(application, dict):
            directory = application.get("directory")
            if not isinstance(directory, str) or path != f"{directory}/result.md":
                self.error(f"{location}.artifactId", "application result panel must reference its own canonical result.md")

    def _validate_group_cycles(self, groups: list[dict[str, Any]]) -> None:
        parents = {
            group["id"]: group["parentGroupId"]
            for group in groups
            if isinstance(group.get("id"), str) and isinstance(group.get("parentGroupId"), str)
        }
        complete: set[str] = set()
        for identifier in parents:
            if identifier in complete:
                continue
            trail: list[str] = []
            positions: dict[str, int] = {}
            current = identifier
            while current in parents and current not in complete:
                if current in positions:
                    cycle = trail[positions[current]:] + [current]
                    self.error("manifest.groups", f"parentGroupId cycle: {' -> '.join(cycle)}")
                    break
                positions[current] = len(trail)
                trail.append(current)
                current = parents[current]
            complete.update(trail)

    def _validate_presentation_results(
        self,
        presentation: dict[str, Any],
        nodes: dict[str, dict[str, Any]],
        artifacts: dict[str, dict[str, Any]],
    ) -> None:
        result_ids = presentation.get("resultNodeIds")
        if not isinstance(result_ids, list):
            return
        for index, identifier in enumerate(result_ids):
            if not isinstance(identifier, str):
                continue
            node = nodes.get(identifier)
            if node is None:
                continue
            location = f"manifest.presentation.resultNodeIds[{index}]"
            node_type = node.get("type")
            if node_type not in {"application", "result"}:
                self.error(location, "returned node must have type 'application' or 'result'")
                continue
            application = node.get("application")
            directory = application.get("directory") if isinstance(application, dict) else None
            expected_path = f"{directory}/result.md" if isinstance(directory, str) else None
            exposes_result = False
            panels = node.get("panels")
            if isinstance(panels, list):
                for panel in panels:
                    if not isinstance(panel, dict) or panel.get("role") != "result":
                        continue
                    artifact = artifacts.get(panel.get("artifactId"))
                    if not isinstance(artifact, dict):
                        continue
                    path = artifact.get("path")
                    role = artifact.get("role")
                    parts = PurePosixPath(path).parts if isinstance(path, str) else ()
                    canonical_application = (
                        role == "application-result"
                        and len(parts) == 3
                        and parts[0] == "applications"
                        and parts[2] == "result.md"
                    )
                    canonical_final = role == "final" and path == "final.md"
                    if node_type == "application" and path == expected_path:
                        exposes_result = True
                        break
                    if node_type == "result" and (canonical_application or canonical_final):
                        exposes_result = True
                        break
            if not exposes_result:
                noun = "application" if node_type == "application" else "result node"
                self.error(
                    location,
                    f"returned {noun} must expose canonical accepted content in a result panel",
                )

    def _safe_relative_path(self, value: str, location: str) -> PurePosixPath | None:
        if not value or value.startswith("/") or value.endswith("/"):
            self.error(location, "must be a normalized relative POSIX path")
            return None
        if "\\" in value or "//" in value or SCHEME_RE.match(value):
            self.error(location, "must be a normalized relative POSIX path without a URL scheme or backslash")
            return None
        path = PurePosixPath(value)
        if any(part in {"", ".", ".."} for part in path.parts):
            self.error(location, "must not contain empty, '.', or '..' segments")
            return None
        if str(path) != value:
            self.error(location, "must be a normalized relative POSIX path")
            return None
        return path

    def _resolve_source_path(self, value: str, location: str, kind: str) -> Path | None:
        relative = self._safe_relative_path(value, location)
        if relative is None:
            return None
        target = self.run_root.joinpath(*relative.parts)
        try:
            resolved = target.resolve(strict=True)
        except (OSError, RuntimeError, ValueError):
            self.error(location, f"referenced {kind} does not exist")
            return None
        if not self._inside_root(resolved):
            self.error(location, f"referenced {kind} resolves outside the run root")
            return None
        if kind == "file" and not resolved.is_file():
            self.error(location, "referenced artifact is not a regular file")
            return None
        if kind == "directory" and not resolved.is_dir():
            self.error(location, "referenced application is not a directory")
            return None
        return resolved

    def _validate_artifact_paths(self, artifacts: list[dict[str, Any]]) -> dict[str, list[int]]:
        paths: dict[str, list[int]] = {}
        for index, artifact in enumerate(artifacts):
            value = artifact.get("path")
            if not isinstance(value, str):
                continue
            paths.setdefault(value, []).append(index)
            location = f"manifest.artifacts[{index}].path"
            relative = self._safe_relative_path(value, location)
            if relative is None:
                continue
            if relative.parts[0] == "view":
                self.error(location, "view/ projection files must not appear in the source inventory")
            if any(part.startswith(".") for part in relative.parts):
                self.error(location, "hidden files must not appear in the source inventory")
            self._resolve_source_path(value, location, "file")
            role = artifact.get("role")
            in_attempts = len(relative.parts) >= 4 and relative.parts[0] == "applications" and relative.parts[2] == "attempts"
            canonical_result = len(relative.parts) == 3 and relative.parts[0] == "applications" and relative.parts[2] == "result.md"
            if in_attempts and role != "attempt":
                self.error(f"manifest.artifacts[{index}].role", "files under application attempts/ must use role 'attempt'")
            if role == "application-result" and not canonical_result:
                self.error(f"manifest.artifacts[{index}].role", "application-result is reserved for canonical applications/<id>/result.md")
            if canonical_result and role != "application-result":
                self.error(f"manifest.artifacts[{index}].role", "canonical application result.md must use role 'application-result'")
        for value, indices in paths.items():
            if len(indices) > 1:
                for index in indices[1:]:
                    self.error(f"manifest.artifacts[{index}].path", f"duplicate inventory path {value!r}")
        return paths

    def _source_files(self) -> set[str]:
        result: set[str] = set()

        def walk(lexical: Path, relative: PurePosixPath, ancestors: frozenset[Path]) -> None:
            try:
                resolved_dir = lexical.resolve(strict=True)
            except (OSError, RuntimeError):
                return
            if not self._inside_root(resolved_dir) or not resolved_dir.is_dir() or resolved_dir in ancestors:
                return
            try:
                entries = sorted(os.scandir(lexical), key=lambda entry: entry.name)
            except OSError as exc:
                self.error(str(relative) or "run", f"cannot inspect source directory: {_exception_text(exc)}")
                return
            next_ancestors = ancestors | {resolved_dir}
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                child_relative = relative / entry.name
                if not relative.parts and entry.name == "view":
                    continue
                child = Path(entry.path)
                try:
                    resolved = child.resolve(strict=True)
                except (OSError, RuntimeError):
                    continue
                if not self._inside_root(resolved):
                    continue
                if resolved.is_file():
                    result.add(child_relative.as_posix())
                elif resolved.is_dir():
                    walk(child, child_relative, next_ancestors)

        walk(self.run_root, PurePosixPath(), frozenset())
        return result

    def _validate_inventory(self, artifact_paths: dict[str, list[int]]) -> None:
        expected = self._source_files()
        actual = set(artifact_paths)
        for path in sorted(expected - actual):
            self.error(f"source:{path}", "missing artifact inventory record")
        for path in sorted(actual - expected):
            if not path.startswith("view/") and not any(part.startswith(".") for part in PurePosixPath(path).parts):
                self.error(f"artifact:{path}", "artifact path is not an inventory-eligible source file")

    def _application_directories(self) -> set[str]:
        applications = self.run_root / "applications"
        if not applications.exists():
            return set()
        try:
            applications_real = applications.resolve(strict=True)
        except (OSError, RuntimeError, ValueError):
            self.error("applications", "applications directory cannot be resolved")
            return set()
        if not self._inside_root(applications_real):
            self.error("applications", "applications directory resolves outside the run root")
            return set()
        if not applications_real.is_dir():
            return set()
        result: set[str] = set()
        try:
            entries = sorted(os.scandir(applications), key=lambda entry: entry.name)
        except OSError as exc:
            self.error("applications", f"cannot inspect applications: {_exception_text(exc)}")
            return set()
        for entry in entries:
            if entry.name.startswith("."):
                continue
            try:
                if not entry.is_dir(follow_symlinks=True):
                    continue
            except (OSError, RuntimeError, ValueError):
                continue
            directory = f"applications/{entry.name}"
            result.add(directory)
            try:
                resolved = Path(entry.path).resolve(strict=True)
            except (OSError, RuntimeError):
                self.error(directory, "application directory cannot be resolved")
                continue
            if not self._inside_root(resolved):
                self.error(directory, "application directory resolves outside the run root")
        return result

    def _validate_applications(self, nodes: list[dict[str, Any]], artifact_paths: dict[str, list[int]]) -> None:
        expected = self._application_directories()
        mapped: dict[str, list[int]] = {}
        for index, node in enumerate(nodes):
            application = node.get("application")
            if not isinstance(application, dict):
                continue
            directory = application.get("directory")
            if not isinstance(directory, str):
                continue
            location = f"manifest.nodes[{index}].application.directory"
            relative = self._safe_relative_path(directory, location)
            if relative is None:
                continue
            if len(relative.parts) != 2 or relative.parts[0] != "applications" or relative.parts[1].startswith("."):
                self.error(location, "must name exactly applications/<application-id>")
                continue
            self._resolve_source_path(directory, location, "directory")
            if node.get("type") != "application":
                continue
            mapped.setdefault(directory, []).append(index)

            canonical_result = f"{directory}/result.md"
            status = node.get("status")
            has_result = canonical_result in artifact_paths
            if status == "succeeded" and not has_result:
                self.error(f"manifest.nodes[{index}].status", f"succeeded application has no canonical {canonical_result}")
            if has_result and status != "succeeded":
                self.error(
                    f"manifest.nodes[{index}].status",
                    "application with a canonical result.md must have status 'succeeded'",
                )

        for directory in sorted(expected - set(mapped)):
            self.error(directory, "runtime application directory has no application node")
        for directory in sorted(set(mapped) - expected):
            self.error(f"application:{directory}", "application node does not map to a runtime application directory")
        for directory, indices in sorted(mapped.items()):
            if len(indices) > 1:
                for index in indices[1:]:
                    self.error(f"manifest.nodes[{index}].application.directory", f"duplicate application mapping for {directory!r}")

    def _validate_notes(self) -> None:
        notes = self.run_root / "view" / "notes.md"
        location = "view/notes.md"
        try:
            resolved = notes.resolve(strict=True)
        except (OSError, RuntimeError):
            self.error(location, "canonical bundle requires notes.md")
            return
        if not self._inside_root(resolved):
            self.error(location, "notes.md resolves outside the run root")
        elif not resolved.is_file():
            self.error(location, "notes.md is not a regular file")


def validate(run_root: Path | str, manifest_path: Path | str | None = None) -> list[str]:
    """Return deterministic diagnostics for one run bundle."""
    root = Path(run_root)
    try:
        root.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        return [f"run: cannot resolve run root: {exc}"]
    if manifest_path is None:
        candidate = root / "view" / "manifest.json"
        canonical = True
    else:
        supplied = Path(manifest_path)
        candidate = supplied if supplied.is_absolute() else root / supplied
        try:
            canonical = candidate.resolve(strict=False) == (root / "view" / "manifest.json").resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            canonical = False
    return Validator(root, candidate, canonical).validate()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", help="explicit Sem run directory")
    parser.add_argument("manifest", nargs="?", help="optional run-relative or absolute candidate manifest path")
    args = parser.parse_args(argv)
    errors = validate(args.run_root, args.manifest)
    if errors:
        encoding = sys.stderr.encoding or "utf-8"
        for diagnostic in errors:
            safe = diagnostic.encode(encoding, errors="backslashreplace").decode(encoding)
            print(safe, file=sys.stderr)
        return 1
    manifest = args.manifest or "view/manifest.json"
    print(f"valid: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
