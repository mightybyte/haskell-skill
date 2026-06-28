#!/usr/bin/env python3
"""Structural validation for the Haskell skills monorepo.

Fast, dependency-free checks (stdlib only) over BOTH skills, run before the expensive
model-graded evals. Mirrors the always-on CI job. Run from anywhere:

    python3 scripts/validate_skill.py

Exits non-zero if any hard check fails.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ["haskell-coder", "haskell-reviewer"]

# These skills are intentionally comprehensive reference guides, so the line guardrail is
# looser than a typical skill — we still want a backstop against runaway growth.
SKILL_LINES_WARN = 600
SKILL_LINES_FAIL = 900

errors: list[str] = []
warnings: list[str] = []


def check_frontmatter(skill: str, skill_dir: Path) -> str:
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        errors.append(f"[{skill}] SKILL.md is missing.")
        return ""
    text = md.read_text(encoding="utf-8")

    if not text.startswith("---"):
        errors.append(f"[{skill}] SKILL.md must begin with a YAML frontmatter block (`---`).")
    else:
        parts = text.split("---", 2)
        if len(parts) < 3:
            errors.append(f"[{skill}] SKILL.md frontmatter block is not closed with a second `---`.")
        else:
            fm = parts[1]
            for key in ("name", "description"):
                if not re.search(rf"^\s*{key}\s*:", fm, re.MULTILINE):
                    errors.append(f"[{skill}] SKILL.md frontmatter is missing required key `{key}`.")
            m = re.search(r"^\s*name\s*:\s*(\S+)", fm, re.MULTILINE)
            if m and m.group(1) != skill:
                warnings.append(f"[{skill}] frontmatter name `{m.group(1)}` differs from directory name.")

    n = len(text.splitlines())
    if n > SKILL_LINES_FAIL:
        errors.append(f"[{skill}] SKILL.md is {n} lines (hard limit {SKILL_LINES_FAIL}). Move detail into references/.")
    elif n > SKILL_LINES_WARN:
        warnings.append(f"[{skill}] SKILL.md is {n} lines (soft target <{SKILL_LINES_WARN}).")
    return text


def check_references(skill: str, skill_dir: Path, skill_text: str) -> None:
    # Every relative reference the skill points to must exist.
    referenced = set(re.findall(r"`?(references/[\w./-]+\.md)`?", skill_text))
    for rel in sorted(referenced):
        if not (skill_dir / rel).is_file():
            errors.append(f"[{skill}] SKILL.md references `{rel}`, but that file does not exist.")
    # And every reference doc on disk should be reachable from SKILL.md (catches orphans/typos).
    ref_dir = skill_dir / "references"
    if ref_dir.is_dir():
        for f in sorted(ref_dir.glob("*.md")):
            rel = f"references/{f.name}"
            if rel not in referenced:
                warnings.append(f"[{skill}] {rel} exists but is not linked from SKILL.md (orphan reference?).")


def check_evals(skill: str, skill_dir: Path) -> None:
    evals_path = skill_dir / "eval-workspace" / "evals" / "evals.json"
    if not evals_path.is_file():
        errors.append(f"[{skill}] eval-workspace/evals/evals.json is missing.")
        return
    try:
        data = json.loads(evals_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"[{skill}] evals.json is not valid JSON: {e}")
        return
    cases = data.get("evals")
    if not isinstance(cases, list) or not cases:
        errors.append(f"[{skill}] evals.json must have a non-empty `evals` array.")
        return
    seen: set = set()
    for i, case in enumerate(cases):
        where = f"[{skill}] evals[{i}]"
        cid = case.get("id")
        if cid is None:
            errors.append(f"{where} is missing `id`.")
        elif cid in seen:
            errors.append(f"{where} has duplicate id {cid!r}.")
        else:
            seen.add(cid)
        if not str(case.get("prompt", "")).strip():
            errors.append(f"{where} is missing a non-empty `prompt`.")


def main() -> int:
    for skill in SKILLS:
        skill_dir = ROOT / skill
        if not skill_dir.is_dir():
            errors.append(f"[{skill}] skill directory is missing.")
            continue
        text = check_frontmatter(skill, skill_dir)
        if text:
            check_references(skill, skill_dir, text)
        check_evals(skill, skill_dir)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"\nOK: structural checks passed for {len(SKILLS)} skills ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
