# learnings/ — local skill-improvement captures

This is the shared local notebook for both skills (`haskell-coder` and `haskell-reviewer`). When you
use a skill and it turns out **wrong, dated, or thin**, drop a short note here. Two things happen
with these notes:

1. **They improve the skills for you immediately.** Next time a skill is used on your codebase, it
   can read accumulated learnings and avoid repeating the mistake — no upstream round-trip needed.
2. **The generalizable ones can flow upstream** to improve the shared, open-source skills for
   everyone — but only through the corroboration gate below.

## Privacy: everything here is local by default

Captures may reference your own code or house conventions, so **this directory is git-ignored** (only
`README.md` and `TEMPLATE.md` are tracked). Nothing you write here is committed or shared unless you
deliberately promote it.

Tag each capture:

- **`local-only`** — reflects a house preference, or you can't corroborate it publicly / by example.
  Stays here. Still valuable on your own codebase.
- **`shareable`** — generalizes to the wider Haskell community *and* you can back it with an
  authoritative public source (the [GHC User's Guide](https://downloads.haskell.org/ghc/latest/docs/users_guide/),
  the [Haskell Report](https://www.haskell.org/onlinereport/haskell2010/), a library's
  [Hackage](https://hackage.haskell.org/) Haddocks, the [PVP](https://pvp.haskell.org/)) **or a
  minimal example that compiles/runs and demonstrates it.**

Haskell's advantage over most ecosystems: a lot of claims are *checkable by building them*. A tiny
reproducing module is often stronger corroboration than a citation — and it can't carry private
detail. Generalize first; if it won't generalize past your team's taste, keep it `local-only`.

## How to capture

Copy `TEMPLATE.md` to `YYYY-MM-DD-short-slug.md` and fill it in. Keep it short — a few lines is
plenty. The goal is a durable, specific lesson, not an essay.

## Promoting a `shareable` learning upstream

Turn it into an **eval-backed change** and open a PR — see `../CONTRIBUTING.md`. In short: add a case
to the relevant skill's `eval-workspace/evals/evals.json` that fails on the current skill and passes
after your edit, make the prose change, include the citation or the reproducing example, and get a
human to approve the merge.
