#!/usr/bin/env python3
"""Flag content-dependent vertical alignment in Haskell code.

Algorithm (per the skill's "Vertical alignment" guidance):

  1. On each line, wherever there is a run of 2+ spaces that has a non-whitespace
     char before it (an *internal* gap, not leading indentation), note the column of
     the first non-whitespace char after the last space of that run.
  2. Store that set of "gap-end columns" per line.
  3. Flag any column shared by 2 or more *consecutive* lines — that's a token padded
     into the same column across adjacent lines, i.e. alignment whose width is a
     function of some identifier's length. Renaming/adding/removing an entry then
     re-spaces its neighbours, bloating diffs.

This is a CANDIDATE finder, not a hard gate. Constant-width padding (e.g. lining up
module names after the fixed `qualified ` keyword) is acceptable and is suppressed.
Diagram art (ASCII trees) and deliberate teaching examples can still trip it — judge
each hit before flagging it to an author.

Usage:
    python3 check_alignment.py File.hs [More.hs ...]     # lint Haskell source
    python3 check_alignment.py --markdown SKILL.md ...    # scan ```...``` fences
    cat File.hs | python3 check_alignment.py -            # stdin

Exit status is 1 if any candidates are found, else 0.
"""
from __future__ import annotations

import re
import sys

# A non-space char, then 2+ spaces, then the gap-end token. group(1) start = the column.
GAP = re.compile(r"\S {2,}(\S)")


def gap_end_cols(line: str) -> set[int]:
    return {m.start(1) for m in GAP.finditer(line.rstrip())}


def is_import_alignment(texts: list[str]) -> bool:
    # Padding plain `import` lines to line up module names after `qualified ` is a
    # fixed, keyword-driven offset — not content-dependent — so it's acceptable.
    code = [t.strip() for t in texts if t.strip()]
    return bool(code) and all(t.startswith("import ") for t in code)


def scan(lines: list[tuple[int, str]], origin: str, out: list[str]) -> int:
    # Map each line number -> its gap-end columns (blank/None lines contribute nothing).
    cols_by_ln: dict[int, set[int]] = {ln: gap_end_cols(t) for ln, t in lines if t.strip()}
    text_by_ln: dict[int, str] = {ln: t for ln, t in lines}

    # For each column, collect the line numbers that have it, then find runs of
    # 2+ CONSECUTIVE line numbers sharing that column.
    col_lines: dict[int, list[int]] = {}
    for ln, cols in cols_by_ln.items():
        for c in cols:
            col_lines.setdefault(c, []).append(ln)

    # block key: (first_line, last_line) -> {columns, line set}
    blocks: dict[tuple[int, int], dict] = {}
    for c, lns in col_lines.items():
        lns.sort()
        run = [lns[0]]
        for x in lns[1:]:
            if x == run[-1] + 1:
                run.append(x)
            else:
                _record(run, c, blocks)
                run = [x]
        _record(run, c, blocks)

    n = 0
    for (a, z), info in sorted(blocks.items()):
        member_texts = [text_by_ln[ln] for ln in range(a, z + 1) if ln in text_by_ln]
        if is_import_alignment(member_texts):
            continue
        n += 1
        cols = sorted(info["cols"])
        marked = info["lines"]
        out.append(f"{origin}:{a}-{z}: vertical alignment at column(s) {cols}")
        for ln in range(a, z + 1):
            if ln in text_by_ln:
                mark = " <--" if ln in marked else ""
                out.append(f"    {ln:>4}: {text_by_ln[ln].rstrip()}{mark}")
        out.append("")
    return n


def _record(run: list[int], col: int, blocks: dict) -> None:
    if len(run) < 2:
        return
    key = (run[0], run[-1])
    b = blocks.setdefault(key, {"cols": set(), "lines": set()})
    b["cols"].add(col)
    b["lines"].update(run)


def md_fences(path: str) -> list[tuple[int, str]]:
    res, infence = [], False
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        s = line.rstrip("\n")
        if s.lstrip().startswith("```"):
            infence = not infence
            res.append((i, ""))          # fence is a block boundary
            continue
        res.append((i, s if infence else ""))
    return res


def main(argv: list[str]) -> int:
    md = "--markdown" in argv
    args = [a for a in argv if a != "--markdown"]
    if not args:
        print(__doc__)
        return 2
    out: list[str] = []
    total = 0
    for path in args:
        if path == "-":
            lines = [(i, l.rstrip("\n")) for i, l in enumerate(sys.stdin, 1)]
            origin = "<stdin>"
        elif md or path.endswith(".md"):
            lines, origin = md_fences(path), path
        else:
            lines = [(i, l.rstrip("\n")) for i, l in enumerate(open(path, encoding="utf-8"), 1)]
            origin = path
        total += scan(lines, origin, out)
    print("\n".join(out).rstrip())
    if total:
        print(f"\n{total} block(s) with content-dependent vertical alignment.")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
