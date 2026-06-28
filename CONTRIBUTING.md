# Contributing to the Haskell Skills

These skills are designed to **improve from collective experience**. Every Haskeller who hits a place
where a skill is wrong, dated, or thin is holding a potential improvement. This document describes the
single, safe path for turning that experience into a change everyone benefits from.

This repo holds two skills — [`haskell-coder`](haskell-coder/SKILL.md) and
[`haskell-reviewer`](haskell-reviewer/SKILL.md) — and they share this one contribution process. Each
skill has its own test suite under `<skill>/eval-workspace/evals/`.

## The one rule: contributions are eval-backed and corroborated

We accept changes as a small bundle we call an **eval-backed change proposal**:

1. **A generalized lesson** — the corrected/added guidance, phrased as a fact useful to the wider
   Haskell community (not your team's house style).
2. **Corroboration** — *either* an authoritative public citation (the
   [GHC User's Guide](https://downloads.haskell.org/ghc/latest/docs/users_guide/), the
   [Haskell Report](https://www.haskell.org/onlinereport/haskell2010/), a library's
   [Hackage](https://hackage.haskell.org/) Haddocks, the [PVP](https://pvp.haskell.org/)) *or* a
   **minimal module that compiles/runs** and demonstrates the point. The reproducing example is often
   the stronger evidence — and it's the most Haskell-native way to settle a disagreement.
3. **An eval that proves it** — a realistic case in the relevant skill's
   `eval-workspace/evals/evals.json` that the *current* skill gets wrong and your edited skill gets
   right. (For `haskell-reviewer`, the case includes the code to be reviewed.)
4. **The prose change** — the edit to the skill's `SKILL.md` or a file under its `references/`.

A change with all four is easy to trust and merge. A change missing the corroboration or the eval will
be asked to add them.

### These skills are opinionated — on purpose

`haskell-coder` and `haskell-reviewer` deliberately recommend *one* good way (ReaderT-over-stacks,
strict-by-default data, `Text`-not-`String`, a conservative `default-extensions` set) rather than
cataloguing every option. A contribution that **adds** missing guidance or **fixes** an error is
easy. A contribution that **revises an opinion** needs to make the case: a concrete, demonstrable
tradeoff, ideally with the reproducing example. "I'd prefer X" isn't enough; "X is faster/safer here's
the benchmark/the type error Y allows" is.

### Why these four

- **Corroboration keeps the skills trustworthy** and keeps house conventions from leaking into shared
  guidance. If you can only back a claim with your own private codebase, it's a `local-only` learning
  (keep it in `learnings/`), not a contribution.
- **The eval is the ratchet.** It documents the failure mode concretely and guards against future
  regressions. We'd rather have a crowd-sourced *test* than crowd-sourced prose — the test makes the
  prose earn its place.

## Workflow

1. **Capture locally first.** Note the issue in `learnings/` (see `learnings/README.md`). Decide if
   it's `local-only` or `shareable`.
2. **Open a friction report** (GitHub issue, "Skill friction report" template) to discuss first — or
   go straight to a PR.
3. **Add/adjust the eval** in the relevant `<skill>/eval-workspace/evals/evals.json`, and confirm the
   *current* skill fails it.
4. **Make the prose change** in that skill's `SKILL.md` or `references/`.
5. **Run validation** (below) and confirm your new eval now passes while the others still do.
6. **Open the PR** using the template, with the corroboration. A maintainer reviews and merges —
   **changes are never auto-merged.**

## Running the checks

Two layers, mirroring CI:

**Structural validation (fast, no API key) — always run this:**

```bash
python3 scripts/validate_skill.py
```

It checks both skills' `SKILL.md` frontmatter, that every `references/...` file each skill points to
exists, that each `eval-workspace/evals/evals.json` parses with the required fields, and basic size
guardrails.

**Model-graded evals (optional, needs an agent + API key):** the full quality comparison — running
each prompt with and without the skill and grading the answers — is driven by the
[`skill-creator`](https://github.com/anthropics/skills) eval harness. It's how maintainers verify a
change actually improves answers without regressing others. CI runs it automatically when an
`ANTHROPIC_API_KEY` secret is available; you don't need it locally to contribute, but it's the gold
standard if you can run it.

## Scope and license

This repo is the **public** skill set. Keep everything in it generic and corroborated. If you're
adapting a skill for a private codebase, do that in your own fork or via local `learnings/` — don't
send house-specific detail upstream. Contributions are accepted under the repository's BSD 3-Clause
license (see [LICENSE](LICENSE)).
