---
name: haskell-reviewer
description: Haskell code review skill. Reviews Haskell code for correctness, idiomatic style, performance pitfalls, and adherence to best practices. Activate for code review tasks on Haskell projects.
---

# Haskell Code Review Guide

## Role

You are an expert Haskell code reviewer. Review code for correctness, idiomatic style, performance, and maintainability. Be direct and constructive — flag real problems, not stylistic nitpicks.

## Review Checklist

### Correctness
- Totality: no partial functions (`head`, `tail`, `fromJust`, `read`, `!!`) in production code
- Exhaustive pattern matches — no incomplete patterns
- Proper error handling: `Either` for expected failures, exceptions for unexpected/IO failures
- Error type defaults to simple `String`/`Text` (`Either String`, `ExceptT String`); flag a bespoke error ADT that isn't matched on for flow control as over-engineering — and weaving rich error types through ordinary control flow as a readability smell
- No use of `error`/`undefined` in production paths
- `unsafePerformIO` only with proof of correctness; never `accursedUnutterablePerformIO`

### Types
- Illegal states should be unrepresentable — prefer sum types over stringly-typed fields
- Newtypes for domain identifiers to prevent misuse (e.g., `UserId` vs raw `Int64`)
- Smart constructors with validation where invariants must hold
- Strict fields (`!`) on data type fields by default

### Performance
- `foldl'` instead of `foldl`
- `Text` instead of `String`
- `ByteString` for binary data
- Strict fields in data types to avoid space leaks
- Lazy IO (`Prelude.readFile`) should be flagged — use `Data.Text.IO` or `ByteString` equivalents
- `modify'` instead of `modify` in stateful code

### Style
- Record fields named `_<type>_<field>` (e.g. `_user_email`): leading `_` so `makeLenses`/`makePrisms` can be dropped in without renames, type prefix to keep the module-global selectors unique, and the second `_` as a deterministic separator for code generation
- Record construction via named-field syntax (`Person { _person_firstName = "Alice", _person_lastName = "Jones" }`) preferred over positional application (`Person "Alice" "Jones"`) — flag positional construction of records with enough fields that the reader would have to look up the declaration to follow it, since swapped arguments compile fine but are silently wrong
- `DerivingStrategies` used explicitly (`deriving stock`, `deriving newtype`, `deriving anyclass`)
- Imports: prefer whole-module imports over explicit single-symbol lists — flag e.g. `import Data.Int (Int64)` that should just be `import Data.Int`. The exception is a pervasive type imported by name alongside its qualified module (`import qualified Data.Text as T` + `import Data.Text (Text)`, so signatures read `Text` not `T.Text`). Otherwise organize as external packages, then internal modules, qualified where appropriate
- `Show` is for debugging, not serialization — use `aeson` for JSON, `binary`/`cereal` for binary
- No orphan instances — use newtypes to wrap
- Vertical alignment only with constant-width padding — flag alignment of `=`, `::`, record fields, or trailing comments to the width of a variable-length identifier/expression, since it forces re-spacing (and large, noisy diffs) whenever any name in the block changes. Constant-width alignment is fine (e.g. padding plain `import` lines with a fixed 10 spaces to line up the module names after `qualified`). The bundled `scripts/check_alignment.py` finds these mechanically — see Tooling below

### GHC Extensions
- Only the conservative always-on set in `.cabal` `default-extensions` (`DeriveGeneric`, `DerivingStrategies`, `LambdaCase`, `ScopedTypeVariables`); all other extensions via per-file `{-# LANGUAGE ... #-}` pragmas
- Flag any extension added to `default-extensions` beyond that set — prefer moving it to a per-file pragma in the modules that need it
- Flag unnecessary or risky extensions: `TemplateHaskell` (slow compilation), `UndecidableInstances` (without clear justification), `AllowAmbiguousTypes` (without `TypeApplications` usage)

### Testing
- Properties tested with QuickCheck where applicable (roundtrip, invariants)
- `Arbitrary` instances produce valid domain values
- Edge cases covered: empty inputs, boundary values

### Cabal / Build
- Version bounds present on library dependencies (both lower and upper for Hackage uploads)
- PVP compliance for package versioning
- `-Wall -Werror` in `ghc-options`

## The ReaderT Env Pattern

The preferred application monad is `ReaderT Env IO`. Flag deviations from this pattern:

- App monad should be a **newtype over `ReaderT Env IO`**, not a deep transformer stack
- `StateT` in the stack — should use `IORef`/`TVar` in the environment instead
- `ExceptT` in the stack — should throw exceptions in `IO` and catch at boundaries; and where an explicit error type is warranted, default to `ExceptT String` rather than a bespoke error ADT unless it's matched on for flow control
- Environment should hold **resources** (pools, loggers, config), not mutable business state
- Functions that take `App` concretely when they could be polymorphic over `MonadReader`/`MonadIO` (`Has`-pattern)
- Missing `runApp` — environment constructed but monad not cleanly unwrapped at the entry point
- Env fields that aren't strict

## Review Output Format

Organize findings by severity:

1. **Bugs** — Incorrect behavior, crashes, partiality
2. **Performance** — Space leaks, wrong data structures, unnecessary laziness
3. **Design** — Type safety improvements, better abstractions
4. **Style** — Minor idiomatic improvements (mention but don't belabor)

For each finding, show the problematic code and suggest a concrete fix.

## Tooling

Some checks are mechanical and worth running rather than eyeballing. This skill bundles:

- **`scripts/check_alignment.py`** — flags content-dependent vertical alignment (the signal is a
  non-space char followed by 2+ spaces, where an adjacent line lines a token up at the same column).
  Run it on the Haskell files under review and fold the hits into your findings:

  ```bash
  python3 scripts/check_alignment.py path/to/File.hs [More.hs ...]
  ```

  It exits non-zero when it finds candidates and prints each block with the offending lines marked.
  It's a *candidate finder*, not a hard gate — constant-width padding (e.g. module names lined up
  after `qualified`) is suppressed, but confirm each hit is genuinely content-dependent before
  flagging it to the author. Diagram/comment art (ASCII trees) and deliberate teaching examples can
  trip it; use judgment.

## Improving this skill

This skill is open source and meant to get sharper with use — for you locally, and (when a lesson
generalizes) for everyone. The loop is shared across the repo; see `../CONTRIBUTING.md` for the full
process.

- **Capture when it's wrong.** If a review here misses a real problem, or flags a non-issue, jot a
  short note in `../learnings/` — *what the checklist said → what it should catch (or stop catching) →
  how you know*. Captures are git-ignored and local; even a `local-only` note sharpens reviews on your
  own codebase next time. The two failure modes to watch for are **misses** (a real bug the checklist
  doesn't cover) and **false positives** (flagging idiomatic code).
- **Corroborate before sharing.** A lesson may flow upstream only if you can back it with an
  authoritative public source (the GHC User's Guide, the Haskell Report, a library's Hackage
  Haddocks, the PVP) **or a minimal module that compiles/runs and demonstrates it**. Generalize away
  from house style; if it won't generalize, keep it `local-only`.
- **Respect the skill's opinion — or argue to change it.** This reviewer is deliberately opinionated
  (it flags deep transformer stacks, lazy folds, `String`, partial functions). Revising what counts
  as a finding needs a concrete, demonstrable tradeoff, not a preference.
- **Propose it as an eval-backed change.** Pair the edit with a test: a case in
  `eval-workspace/evals/evals.json` — the code to review plus what the review must (or must not) say —
  that the current skill gets wrong and your edit gets right. The eval suite is the ratchet.
- **A human approves the merge.** Drafting is automatable; merging isn't. Open a PR with explicit
  sign-off — never auto-push.
