# Haskell Skills

Comprehensive [Agent Skills](https://agentskills.io) for professional Haskell development and code review. Built by senior Haskell developers and community leaders with years of production Haskell experience, these skills encode the patterns, practices, and hard-won knowledge that define modern, industrial-strength Haskell.

## Skills

This repository contains two complementary skills:

### haskell-coder

Expert Haskell development skill. Gives any compatible coding agent deep expertise in Haskell programming, from project setup through production deployment. It reflects the way experienced Haskell engineers actually write code: type-driven, pragmatic, and grounded in real-world tradeoffs.

The skill follows a progressive disclosure architecture. The main `SKILL.md` provides immediately actionable guidance (~420 lines), while seven deep-dive reference documents cover advanced topics agents can load on demand.

**Covers:**

- Project setup and structure (Cabal 3.0)
- Essential GHC extensions (categorized: always-on, use-freely, avoid-unless-needed)
- Type-driven development patterns (newtypes, phantom types, smart constructors)
- Error handling
- Testing with HSpec and QuickCheck
- Performance essentials (strictness, profiling, space leak prevention)
- Common gotchas that trip up even intermediate Haskellers
- Key library recommendations across 18 packages
- Commands reference for the full build/test/profile lifecycle

**Reference Documents:**

| File | Topics |
|------|--------|
| [`references/type-system.md`](haskell-coder/references/type-system.md) | ADTs, GADTs, type families, type classes, DataKinds, phantom types |
| [`references/common-patterns.md`](haskell-coder/references/common-patterns.md) | MTL, ReaderT, effect systems, optics, free monads, type-level programming |
| [`references/libraries.md`](haskell-coder/references/libraries.md) | Essential library ecosystem with usage examples |
| [`references/performance.md`](haskell-coder/references/performance.md) | Strictness, profiling, space leaks, concurrency, benchmarking with Criterion |
| [`references/ghc-extensions.md`](haskell-coder/references/ghc-extensions.md) | 30+ GHC extensions documented with examples and safety guidance |
| [`references/cabal-guide.md`](haskell-coder/references/cabal-guide.md) | Cabal format, multi-package projects, CI/CD, Hackage publishing |
| [`references/nix-haskell.md`](haskell-coder/references/nix-haskell.md) | Nix-based Haskell development (nixpkgs, haskell.nix, haskell-flake) |

### haskell-reviewer

Haskell code review skill. Reviews code for correctness, idiomatic style, performance pitfalls, and adherence to best practices. Covers totality, type safety, strictness, GHC extension usage, testing, and build configuration.

## Installation

### Claude Code

Add individual skills as dependencies in your project's `.claude/settings.json`:

```json
{
  "skills": [
    "github:mightybyte/haskell-skill/haskell-coder",
    "github:mightybyte/haskell-skill/haskell-reviewer"
  ]
}
```

Or install them directly:

```
/skill add github:mightybyte/haskell-skill/haskell-coder
/skill add github:mightybyte/haskell-skill/haskell-reviewer
```

### OpenClaw

Install from [ClawHub](https://clawhub.ai/):

```bash
npx clawhub@latest install haskell-coder
npx clawhub@latest install haskell-reviewer
```

Or via the OpenClaw CLI:

```bash
clawhub install haskell-coder
clawhub install haskell-reviewer
```

### Cursor

Add to your Cursor rules or `.cursor/skills/` directory. See [Cursor's Agent Skills documentation](https://docs.cursor.com/context/agent-skills) for details.

### Other Compatible Agents

These skills follow the open [Agent Skills specification](https://agentskills.io/specification). Any agent that supports the spec can use them. Clone or download the repository and point your agent's skill configuration to the relevant `SKILL.md` file.

## Compatibility

- **GHC**: 9.2+ (some features reference GHC 9.2+ syntax like `OverloadedRecordDot`, but this is easily overridable)
- **Build system**: Cabal 3.0+
- **Language standard**: Haskell2010 as the base, with curated extensions

## Core Philosophy

1. **Types are the design** -- Make illegal states unrepresentable
2. **Purity by default** -- Side effects are explicit in the type system
3. **Laziness as a tool** -- Elegant abstractions with awareness of space leaks
4. **Correctness first, then performance** -- Get it right, profile, then optimize
5. **Keep it simple** -- Haskell2010 + purity + strong types deliver the majority of the value

## Design Principles

These skills are intentionally opinionated. Rather than presenting every possible approach, they capture what works in production:

- **Pragmatic over academic** -- Recommends the simplest abstraction that solves the problem. Discourages reaching for advanced type machinery unless it pays for itself.
- **Battle-tested patterns** -- Every recommendation has been validated in real-world codebases. The ReaderT pattern, strict-by-default data types, Text-not-String -- these aren't theoretical preferences.
- **Progressive complexity** -- Agents start with the core instructions and pull in reference material only when the task demands it. Simple tasks stay simple.
- **Guardrails included** -- Explicit "avoid" lists for extensions, functions, and patterns that cause problems in practice. Twelve common gotchas that prevent the mistakes teams actually make.

## Contributing

These skills are built to **improve from collective experience**, through one safe, eval-backed loop.
When a skill is wrong, dated, or thin, the path is: capture the lesson, corroborate it (an
authoritative citation *or* a minimal module that compiles and demonstrates the point), add a test
case that the current skill fails and your fix passes, make the prose edit, and open a PR. A
maintainer reviews and merges — changes are never auto-merged. See **[CONTRIBUTING.md](CONTRIBUTING.md)**
for the full process.

Supporting structure:

```
CONTRIBUTING.md              The eval-backed, corroborated change process (covers both skills).
learnings/                   Local skill-improvement captures (git-ignored; never committed).
scripts/validate_skill.py    Fast structural checks (frontmatter, reference links, evals.json).
.github/                     Issue/PR templates + CI workflow (the eval ratchet).
<skill>/eval-workspace/
  evals/evals.json           The skill's test suite — tracked; this is source.
  iteration-*/, ...          Generated run output — git-ignored.
```

Run `python3 scripts/validate_skill.py` before opening a PR. Because these skills are intentionally
opinionated, a change that *revises* a recommendation should make the case with a concrete tradeoff,
not just a preference.

## License

BSD 3-Clause. See [LICENSE](LICENSE) for details.
