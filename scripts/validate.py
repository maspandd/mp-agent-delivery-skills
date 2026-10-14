#!/usr/bin/env python3
"""Validate every skill in skills/ against the Agent Skills specification.

Spec: https://agentskills.io/specification
Also checks .claude-plugin/marketplace.json for the fields Claude Code requires.

Usage: python3 scripts/validate.py [repo_root]
Exit code 0 when no errors, 1 when any error is found. Warnings do not fail.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is missing. Install it with: pip install pyyaml")

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
BODY_LINES_MAX = 500
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """Return (frontmatter, body), or None when the file has no frontmatter block."""
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if match is None:
        return None
    return match.group(1), match.group(2)


def check_name(name: object, folder: str, where: str, report: Report) -> None:
    if not isinstance(name, str) or not name:
        report.errors.append(f"{where}: 'name' is missing or empty")
        return
    if len(name) > NAME_MAX:
        report.errors.append(f"{where}: 'name' has {len(name)} characters, maximum is {NAME_MAX}")
    if NAME_PATTERN.fullmatch(name) is None:
        report.errors.append(f"{where}: 'name' must use a-z, 0-9 and single hyphens only")
    if name != folder:
        report.errors.append(f"{where}: 'name' is '{name}' but the folder is '{folder}'")


def check_optional_fields(meta: dict, where: str, report: Report) -> None:
    compatibility = meta.get("compatibility")
    if compatibility is not None and (not isinstance(compatibility, str) or not 1 <= len(compatibility) <= COMPATIBILITY_MAX):
        report.errors.append(f"{where}: 'compatibility' must be 1-{COMPATIBILITY_MAX} characters")
    metadata = meta.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()):
            report.errors.append(f"{where}: 'metadata' must map strings to strings (quote numbers, e.g. \"1.0\")")
    for key in sorted(set(meta) - SPEC_FIELDS):
        report.warnings.append(f"{where}: field '{key}' is not in the open spec; some agents ignore it")


def check_skill(skill_dir: Path, report: Report) -> None:
    where = f"skills/{skill_dir.name}/SKILL.md"
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        report.errors.append(f"{where}: file not found (the name must be SKILL.md, upper case)")
        return
    parts = split_frontmatter(skill_file.read_text(encoding="utf-8"))
    if parts is None:
        report.errors.append(f"{where}: no YAML frontmatter between '---' lines")
        return
    frontmatter, body = parts
    try:
        meta = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        report.errors.append(f"{where}: frontmatter is not valid YAML: {exc}")
        return
    if not isinstance(meta, dict):
        report.errors.append(f"{where}: frontmatter must be a YAML mapping")
        return
    check_name(meta.get("name"), skill_dir.name, where, report)
    description = meta.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= DESCRIPTION_MAX:
        report.errors.append(f"{where}: 'description' must be 1-{DESCRIPTION_MAX} characters")
    check_optional_fields(meta, where, report)
    body_lines = len(body.splitlines())
    if body_lines > BODY_LINES_MAX:
        report.warnings.append(f"{where}: body has {body_lines} lines; the spec recommends under {BODY_LINES_MAX}")


def check_marketplace(root: Path, report: Report) -> None:
    path = root / ".claude-plugin" / "marketplace.json"
    if not path.is_file():
        report.warnings.append(".claude-plugin/marketplace.json not found; Claude Code plugin install will not work")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.errors.append(f"marketplace.json: invalid JSON: {exc}")
        return
    for key in ("name", "owner", "plugins"):
        if key not in data:
            report.errors.append(f"marketplace.json: required field '{key}' is missing")
    for index, plugin in enumerate(data.get("plugins", [])):
        if "name" not in plugin or "source" not in plugin:
            report.errors.append(f"marketplace.json: plugins[{index}] needs 'name' and 'source'")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    skills_root = root / "skills"
    if not skills_root.is_dir():
        print(f"ERROR: {skills_root} not found")
        return 1
    report = Report()
    skill_dirs = sorted(p for p in skills_root.iterdir() if p.is_dir() and not p.name.startswith("."))
    for skill_dir in skill_dirs:
        check_skill(skill_dir, report)
    check_marketplace(root, report)
    for warning in report.warnings:
        print(f"WARN  {warning}")
    for error in report.errors:
        print(f"ERROR {error}")
    print(f"Checked {len(skill_dirs)} skill(s): {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
