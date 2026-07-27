---
name: haskell-coder
description: Expert Haskell development skill. Covers type-driven design, GHC extensions, Cabal/Nix builds, performance optimization, testing, and the modern Haskell library ecosystem. Activate for any Haskell programming, debugging, or architecture tasks.
---

# Haskell Development Guide

## Core Philosophy

1. **Types are the design** — Make illegal states unrepresentable. If the type checker accepts it, we would like it to be correct.
2. **Prefer Purity** — Put as much code into pure functions as possible.  Also, `IO` is a feature, not a burden.
3. **Laziness as a tool** — Enables elegant abstractions but demands awareness of space leaks.
4. **Correctness first, then performance** — Get it right, then profile, then optimize.
5. **Keep it Simple** — Purity and strong types (i.e. roughly Haskell2010) gives you the majority of Haskell's value.  Avoid more advanced language features unless absolutely necessary.

## Project Setup

### Cabal (preferred with Nix)

```bash
mkdir my-project && cd my-project
cabal init --interactive
```

Minimal `my-project.cabal`:
```cabal
cabal-version: 3.0
name: my-project
version: 0.1.0.0
build-type: Simple

common warnings
    ghc-options: -Wall -Werror -Wcompat -Widentities
                 -Wincomplete-record-updates
                 -Wincomplete-uni-patterns
                 -Wpartial-fields
                 -Wredundant-constraints

library
    import: warnings
    exposed-modules: MyProject
    build-depends:
      base >= 4.17 && < 5,
      text,
      containers,
      aeson,
    hs-source-dirs: src
    default-language: Haskell2010
    default-extensions:
      DeriveGeneric
      DerivingStrategies
      LambdaCase
      ScopedTypeVariables

executable my-project
    import: warnings
    main-is: Main.hs
    build-depends: base, my-project
    hs-source-dirs: exe
    default-language: Haskell2010

test-suite tests
    import: warnings
    type: exitcode-stdio-1.0
    main-is: Main.hs
    build-depends:
      base,
      my-project,
      hspec,
      QuickCheck
    hs-source-dirs: test
    default-language: Haskell2010
```

Package version bounds go in the cabal file.  Libraries uploaded to hackage
should have both lower and upper bounds reflecting verified builds-successfully
status. Package versions should conform to the Haskell Package Versioning
Policy (PVP, https://pvp.haskell.org/).  Packaging providing an executable
and no package for upload to hackage don't need to specify version bounds.

## Project Structure

```
my-project/
├── exe/
│   └── Main.hs              # Executable entry point (thin — delegates to library)
├── src/
│   ├── MyProject.hs          # Public API (re-exports)
│   ├── MyProject/
│   │   ├── Types.hs          # Core domain types
│   │   ├── App.hs            # Application monad, config
│   │   ├── DB.hs             # Database layer
│   │   ├── API.hs            # HTTP/API layer
│   │   └── Internal/         # Not exported — implementation details
│   │       └── Utils.hs
├── test/
│   ├── Main.hs
│   └── MyProject/
│       ├── TypesSpec.hs
│       └── DBSpec.hs
├── my-project.cabal
├── cabal.project             # Multi-package config, source-repository-packages
```

## Imports

### Policy: import whole modules, not individual symbols

Prefer importing an entire module over listing explicit symbols:

```haskell
-- PREFERRED
import Control.Monad.Reader
import App.Types.Env
import Data.IORef

-- AVOID
import Control.Monad.Reader (asks, MonadReader, ReaderT, runReaderT)
import App.Types.Env (Env(..), mkEnv)
import Data.IORef (IORef, newIORef, readIORef, modifyIORef')
```

Rationale:

- **Smaller diffs.** Adding, removing, or renaming a used symbol doesn't touch the import line, so edits stay localized to the body of the module.
- **Fewer tool calls.** An editor (or agent) changing call sites doesn't have to also patch the import list — one fewer round-trip per change.
- **Less churn.** Import lists tend to rot; whole-module imports are stable over the life of a module.

Caveats / when explicit imports are still appropriate:

- **Name clashes.** If two modules export the same name and you need both, qualify one (`import qualified Data.Map as M`) or import the other explicitly to surface what's being shadowed.
- **`qualified` imports.** Always use `qualified` with an alias for modules you intend to use prefixed (`import qualified Data.Text as T`). For a *pervasive type* it's idiomatic to also import the bare type name explicitly alongside the qualified module, so signatures read `Text` rather than `T.Text`:
  ```haskell
  import qualified Data.Text as T
  import Data.Text (Text)
  ```
  This explicit-name exception is reserved for a few ubiquitous types like `Text`. For everything else, still prefer the whole-module import — `import Data.Int`, not `import Data.Int (Int64)`.
- **Prelude replacements.** A `NoImplicitPrelude` module should explicitly list what it re-exports from its chosen prelude.  Alternative Preludes are strongly discouraged.  They can significantly change coding patterns from what LLMs expect.
- **Large, overlapping namespaces.** For modules like `Control.Lens` or `Data.Aeson`, it's acceptable to hide a specific operator with `hiding` (e.g. `import Control.Lens hiding ((.=))`) rather than enumerating everything you need.

As a rule of thumb: start with a whole-module import; switch to an explicit list only when there's a concrete reason for that module.

## Vertical alignment

Add alignment spacing only when the padding is a **constant** width. Never align to the width of a
**variable-length construct** — an identifier, type name, or expression. When a column's position
tracks the longest name in a block, adding, renaming, or removing a single entry re-spaces every other
line, inflating the diff (and the tokens an agent spends reading and rewriting it) far out of
proportion to the change, for a purely cosmetic gain. This covers padding that aligns `=`, `::`, `->`,
or trailing comments into columns — including the `::` in a record's fields. Writing records one field
per line with a single space before `::` is the normal, encouraged style; it's only the extra column
padding that's the problem.

```haskell
-- AVOID: the `::` is padded to the longest field, so adding/renaming a field re-aligns every line
data Person = Person
  { _person_firstName :: Text
  , _person_age :: Int
  } deriving (Eq, Ord, Show, Read)

-- PREFER: a single space before each `::` — adding or renaming a field is a one-line diff
data Person = Person
  { _person_firstName :: Text
  , _person_age :: Int
  } deriving (Eq, Ord, Show, Read)
```

Constant-width indentation (a fixed number of leading spaces) is fine — it's only *content-dependent*
alignment, where the spacing is a function of some identifier's length, that causes the churn.

A good example of *acceptable* alignment is padding plain `import` lines with a fixed 10 extra spaces
(the width of `qualified `) so the module names line up. The offset is fixed by the keyword, not by
any identifier, so adding or removing an import never re-spaces the other lines:

```haskell
import qualified Data.Text as T
import           Data.Text (Text)
import           Control.Monad
```

## Essential GHC Extensions

### Policy: prefer per-file `LANGUAGE` pragmas over `default-extensions`

Extensions should **not** be added to `default-extensions` in general. Only a
small, conservative set is desirable to have enabled all the time (listed
below). Everything else should be enabled with a per-file `{-# LANGUAGE ... #-}`
pragma in the module that actually needs it. This keeps the effect of each
extension localized and easy to audit, and avoids forcing extensions that are
risky or situation-specific (e.g. `OverloadedStrings`, `TemplateHaskell`,
`GeneralizedNewtypeDeriving`) on every module in a component.

### Always Enable (via `default-extensions` in .cabal)
```haskell
DeriveGeneric
DerivingStrategies
LambdaCase
ScopedTypeVariables
```

### Enable per-file with a `{-# LANGUAGE ... #-}` pragma when needed
```haskell
BangPatterns
DeriveDataTypeable
DeriveFunctor
DerivingVia
ExistentialQuantification
FlexibleContexts
FlexibleInstances
FunctionalDependencies
GeneralizedNewtypeDeriving
MultiParamTypeClasses
NumericUnderscores
OverloadedStrings
RankNTypes
RecordWildCards
TemplateHaskell
```

### Avoid unless there's a significant clear value
```haskell
GADTs
TypeFamilies
DataKinds
ConstraintKinds
UndecidableInstances
TypeOperators
DuplicateRecordFields
AllowAmbiguousTypes
```

## Type-Driven Development

### Scope accessors with type name to avoid name clashes

```
data User = User
  { _user_firstName :: String
  , _user_email :: String
  } deriving (Eq,Ord,Show,Read,Generic)
```

The `_<type>_<field>` scheme is deliberate on three counts:

- **Leading underscore** — `lens`'s `makeLenses` / `makePrisms` only generate optics for fields that
  start with `_` (from `_user_email` you get a `user_email` lens). Naming fields this way from the
  start means you can drop in `makeLenses ''User` later without renaming any fields or touching call
  sites — no sweeping rename to "add lenses."
- **Type prefix** — record selectors are top-level functions with *module-global* scope, so two types
  with a `name` field would clash. Prefixing with the type name keeps every selector unique.
- **A second underscore between type and field** — it's a deterministic separator, so `_user_email`
  can be split mechanically (`_<type>_<field>`) to recover the owning type. That makes the scheme
  introspectable for code generation, rather than guessing where the type name ends.

### Construct records with named-field syntax

Prefer the named-field (record) constructor syntax over positional application — especially as a
data type grows beyond a couple of fields. Named construction labels each argument at the call site,
so the reader doesn't have to hold the field order in their head and an omitted or swapped argument
is obvious.

```haskell
-- PREFER: each argument is labelled; order is irrelevant and omissions stand out
alice :: Person
alice = Person { _person_firstName = "Alice", _person_lastName = "Jones" }

-- AVOID (especially with many fields): the reader must memorise the declaration's field order,
-- and a swapped argument compiles fine but is silently wrong
alice = Person "Alice" "Jones"
```

For two- or three-field records the positional form is tolerable, but reach for named construction
as soon as the type has enough fields that you'd have to look up the declaration to read the call
site. The same applies to `RecordWildCards`-style updates — prefer naming the fields you're setting.

### Make Illegal States Unrepresentable
```haskell
-- BAD: stringly-typed
data User = User { _user_role :: String, _user_email :: String }

-- GOOD: types encode constraints
data Role = Admin | Editor | Viewer
  deriving stock (Show, Eq, Ord)

newtype Email = Email { _unEmail :: Text }  -- smart constructor validates

-- Plain String error: it's only reported, not matched on for flow control.
mkEmail :: Text -> Either String Email
mkEmail t
  | "@" `T.isInfixOf` t = Right (Email t)
  | otherwise = Left "email must contain '@'"

data User = User
  { _user_role  :: !Role
  , _user_email :: !Email
  }
```

### Phantom Types for State Machines
```haskell
data Draft
data Published

data Article (s :: Type) = Article
  { articleTitle :: !Text
  , articleContent :: !Text
  }

publish :: Article Draft -> Article Published
publish (Article t c) = Article t c

-- Only published articles can be shared
share :: Article Published -> IO ()
share = ...
```

### Newtypes for Safety
```haskell
newtype UserId    = UserId { unUserId :: Int64 }
  deriving newtype (Eq, Ord, Show, FromJSON, ToJSON)
newtype ProductId = ProductId { unProductId :: Int64 }
  deriving newtype (Eq, Ord, Show, FromJSON, ToJSON)

-- Now you can't accidentally pass a ProductId where UserId is expected
getUser :: UserId -> IO User
```

## Error Handling

**Default to simple `String`/`Text` errors.** For the common case — an error that's only reported or
logged, never matched on — use `Either String` (or `ExceptT String`). Reach for a bespoke error ADT
only once the program actually pattern-matches on the error to drive control flow. A typed error
that's just shown to a user is over-engineering: it adds threading friction for no payoff, and weaving
rich error types through ordinary control flow tends to hurt readability. Start with `String`;
introduce a typed error only when you have a clear flow-control need.

```haskell
-- Pure errors: Either — default to a plain String message
parseConfig :: Text -> Either String Config

-- App-level errors: ExceptT or MonadError
class Monad m => MonadError e m where
  throwError :: e -> m a
  catchError :: m a -> (e -> m a) -> m a

-- The ReaderT pattern (simple, composable)
newtype App a = App { unApp :: ReaderT AppEnv IO a }
  deriving newtype (Functor, Applicative, Monad, MonadIO, MonadReader AppEnv)

-- A typed error EARNS its keep here only if you match on it (e.g. map to an HTTP
-- status). If you just log it, Either String / ExceptT String is simpler.
data AppError
  = NotFound Text
  | Unauthorized
  | ValidationError [Text]
  deriving stock (Show)

-- Throw with exceptions in IO, catch at boundaries
throwIO :: Exception e => e -> IO a
catch   :: Exception e => IO a -> (e -> IO a) -> IO a

-- RULE: Use Either for expected failures, exceptions for unexpected/IO failures.
-- Default the error type to String; only reach for a sum type when you match on it.
-- Never use error/undefined in library code.
```

## Common Patterns

### The ReaderT Env Pattern

The preferred application monad is `ReaderT Env IO`. It solves a fundamental problem: most application functions need access to shared context — a database pool, a logger, configuration — and threading these as explicit arguments everywhere is noisy and brittle. The environment gathers all of these common resources into one place so they're available uniformly throughout the application.

Think of it as two architectural layers working together:

- **Uniformity layer (the `AppEnv` record):** The top-level environment collects all the resources and configuration an application commonly needs into a single, concrete type. Rather than passing five separate arguments or defining a bespoke record for every combination, you have one environment that travels everywhere through `ReaderT`. It's the answer to "where do I put things the app needs?"

- **Least-context layer (the `Has` constraints):** Individual functions don't take the full environment — they constrain on only what they actually use. A function that only needs a database pool says so in its type. This keeps functions honest about their dependencies, makes them easier to test in isolation, and means the full `AppEnv` is an implementation detail that most of the codebase doesn't couple to.

There are many possible subsets of the environment that different functions might need. You could try to model every subset as its own type, but that's impractical. The `ReaderT Env` + `Has` combination strikes a good balance: one concrete environment for uniformity at the top, granular constraints for least-context at the bottom.

#### Structure

```haskell
-- The environment holds resources and config, not mutable business state.
data AppEnv = AppEnv
  { appDbPool :: !Pool Connection
  , appLogger :: !Logger
  , appConfig :: !Config
  }

-- Newtype over ReaderT Env IO. Avoid deeper transformer stacks —
-- use IORef/TVar in the env for mutable state, exceptions for errors.
newtype App a = App (ReaderT AppEnv IO a)
  deriving newtype (Functor, Applicative, Monad, MonadIO, MonadReader AppEnv)

-- Unwrap once at the top level.
runApp :: AppEnv -> App a -> IO a
runApp env (App m) = runReaderT m env
```

#### Has-pattern for granular access

```haskell
class Has field env where
  obtain :: env -> field

instance Has (Pool Connection) AppEnv where
  obtain = appDbPool

-- Declares exactly what it needs — not coupled to AppEnv.
grabPool :: (MonadReader env m, Has (Pool Connection) env) => m (Pool Connection)
grabPool = asks obtain
```

#### What to avoid

- **Deep transformer stacks** — `ExceptT AppError (StateT AppState (ReaderT AppEnv IO))` adds complexity and overhead. `ReaderT Env IO` is almost always sufficient.
- **`StateT` in the stack** — use an `IORef`/`TVar` in the environment instead.
- **`ExceptT` in the stack** — throw exceptions in `IO`, catch at boundaries.
- **Mutable business state in the env** — the env holds resources (pools, loggers, config), not application data like `IORef [User]`.

### Optics (lens/optics)
```haskell
-- With OverloadedRecordDot (GHC 9.2+), often you don't need lens for simple access.
-- Use lens/optics for: nested updates, traversals, prisms for sum types.

-- lens: view, set, over
view _1 (1, 2) -- 1
set _1 10 (1, 2) -- (10, 2)
over _1 (+1) (1, 2) -- (2, 2)

-- Compose with (.)
view (config . database . host) appEnv
over (users . each . name) T.toUpper myData
```

## Testing

### HSpec - Testing Framework
```haskell
-- test/MyProject/TypesSpec.hs
module MyProject.TypesSpec (spec) where

import Test.Hspec
import MyProject.Types

spec :: Spec
spec = do
  describe "mkEmail" $ do
    it "accepts valid emails" $
      mkEmail "user@example.com" `shouldBe` Right (Email "user@example.com")

    it "rejects invalid emails" $
      mkEmail "invalid" `shouldSatisfy` isLeft
```

### QuickCheck - Property Testing
```haskell
import Test.QuickCheck

prop_reverseReverse :: [Int] -> Bool
prop_reverseReverse xs = reverse (reverse xs) == xs

-- Generate domain types:
instance Arbitrary Email where
  arbitrary = do
    user   <- listOf1 (elements ['a'..'z'])
    domain <- listOf1 (elements ['a'..'z'])
    pure $ Email $ T.pack $ user <> "@" <> domain <> ".com"
```

## Performance Essentials

### Strictness
```haskell
-- Strict fields in data types (almost always want this):
data Config = Config
  { configHost :: !Text       -- strict (bang pattern in field)
  , configPort :: !Int
  }

-- BangPatterns in let bindings:
{-# LANGUAGE BangPatterns #-}
let !result = expensiveComputation

-- Use Text, not String. Always.
-- Use ByteString for binary data.
-- Use Vector for indexed access, [] for sequential processing.
-- Use HashMap/HashSet for large unordered collections.
-- Use Map/Set for ordered collections or when Ord is available.
```

### Profiling
```bash
# Build with profiling
cabal build --enable-profiling

# Run with heap profiling
./my-project +RTS -hc -p -RTS

# Time profiling report
./my-project +RTS -p -RTS
# Generates my-project.prof

# Heap profile visualization
hp2ps -c my-project.hp
```

### Common Space Leaks
```haskell
-- BAD: lazy accumulator
foldl (+) 0 [1..1000000]  -- builds giant thunk chain

-- GOOD: strict left fold
foldl' (+) 0 [1..1000000]  -- evaluates as it goes

-- BAD: lazy state
modify (\s -> s { count = count s + 1 })  -- thunk builds up

-- GOOD: strict state
modify' (\s -> s { count = count s + 1 })
-- Or: use strict fields + evaluate
```

## Commands Reference

| Task | Command |
|------|---------|
| Build | `cabal build` |
| Run | `cabal run my-project` |
| Test | `cabal test --test-show-details=direct` |
| REPL | `cabal repl` |
| Docs | `cabal haddock` |
| Lint | `hlint src/` |
| File watch | `ghcid --command="cabal repl"` |
| Deps outdated | `cabal outdated` |
| Clean | `cabal clean` |
| Nix full package build | `nix build` |
| Nix faster incremental build | `nix develop --command cabal build` |
| Nix dev shell | `nix develop` |

## Common Gotchas

1. **String is [Char]** — Use `Text` (from `text` package) everywhere. Enable `OverloadedStrings` (per-file pragma) for Text string literals.
2. **Lazy IO** — `readFile` from Prelude is lazy. Use `Data.Text.IO.readFile` or `ByteString.readFile` instead.
3. **Orphan instances** — Don't define typeclass instances outside the module that defines the type or the class. Use newtypes to wrap.
4. **Cabal hell** — Use Nix or cabal's built-in solver (v2-build). Don't use `cabal-install` v1 commands.
5. **Records** — Field names are global. Prefix field names with a uniform and readable scheme: `_employee_familyName`.
6. **Partial functions** — Never use `head`, `tail`, `fromJust`, `read` in production code. Use pattern matching or safe alternatives.
7. **Unsafe operations** - Never use `accursedUnutterablePerformIO`. Only use `unsafePerformIO` when you can prove its use correct.
8. **Undefined** - `undefined` is a fantastic tool for stubbing things out for incremental development and type checking.  It should never exist in production code.
9. **foldl vs foldl'** — Always use `foldl'` (strict). The lazy `foldl` from Prelude is almost never what you want.
10. **Show for serialization** — `Show` is for debugging. Use `aeson` for JSON, `binary`/`cereal` for binary serialization.
11. **MonadFail** — Pattern match failures in `do` blocks require `MonadFail`. Avoid partial patterns in `do`.
12. **Template Haskell ordering** — TH splices create declaration groups. All TH splices must come after the declarations they reference and before declarations that reference the generated code.
13. **Using newer dependencies** - When there is a version mismatch, try upgrading to a newer version first. With cabal or nix flakes, you can put an allow-newer in the `cabal.project` file.

## Hackage Package Repository

The definitive source of published Haskell packages. Contains docs, dependencies, version bounds, etc.

- **Link to most recent version of a package** - https://hackage.haskell.org/package/<PACKAGE> i.e. (https://hackage.haskell.org/package/lens)
- **Link to specific package version** - https://hackage.haskell.org/package/<PACKAGE>-<VERSION> i.e. (https://hackage.haskell.org/package/lens-5.3.4)

## Key Libraries

| Library | Purpose |
|---------|---------|
| `text` | Unicode text (strict & lazy) |
| `bytestring` | Binary data |
| `aeson` | JSON encoding/decoding |
| `postgresql-simple`, `mysql-simple` | Low-level database library |
| `lens` / `optics` | Composable getters/setters |
| `mtl` | Monad transformer classes |
| `containers` | Map, Set, Seq (ordered) |
| `unordered-containers` | HashMap, HashSet (fast) |
| `vector` | Efficient arrays |
| `conduit` / `streaming` | Streaming data processing |
| `warp` | Fast HTTP server |
| `http-client` | Library for making http requests |
| `stm` | Software transactional memory |
| `QuickCheck` | Property-based testing |
| `hspec` | BDD-style test framework |
| `tasty` | Test framework (composable) |
| `criterion` | Benchmarking |
| `optparse-applicative` | CLI argument parsing |
| `katip` | Structured logging |
| `fake` | Generating realistic mock data |

## References

For detailed information, see:
- `references/type-system.md` — ADTs, GADTs, type families, type classes, DataKinds, phantom types
- `references/common-patterns.md` — MTL, ReaderT, effect systems, optics, free monads, type-level programming
- `references/libraries.md` — Essential library ecosystem with examples
- `references/performance.md` — Strictness, profiling, space leaks, concurrency, benchmarking
- `references/ghc-extensions.md` — Comprehensive GHC extension guide by category
- `references/nix-haskell.md` — Nix-based Haskell development (nixpkgs + haskell.nix)
- `references/cabal-guide.md` — Cabal format, multi-package projects, Hackage publishing
- `references/best-practices.md` — Code organization, Haddock, CI, style guide

## Improving this skill

This skill is open source and meant to get sharper with use — for you locally, and (when a lesson
generalizes) for everyone. The loop is shared across the repo; see `../CONTRIBUTING.md` for the full
process.

- **Capture when it's wrong.** If you follow this guidance and it turns out mistaken, dated, or thin,
  jot a short note in `../learnings/` — *what the skill said → what's actually better → how you know*.
  Captures are git-ignored and local; even a `local-only` note sharpens the skill on your own
  codebase next time.
- **Corroborate before sharing.** A lesson may flow upstream only if you can back it with an
  authoritative public source (the GHC User's Guide, the Haskell Report, a library's Hackage
  Haddocks, the PVP) **or a minimal module that compiles/runs and demonstrates it**. In Haskell the
  reproducing example is often the strongest evidence — and it carries no private detail. Generalize
  away from house style; if it won't generalize, keep it `local-only`.
- **Respect the skill's opinion — or argue to change it.** This guide is deliberately opinionated
  (ReaderT-over-stacks, strict-by-default, `Text`-not-`String`, a conservative `default-extensions`
  set). Revising an opinion needs a concrete, demonstrable tradeoff, not a preference.
- **Propose it as an eval-backed change.** Pair the edit with a test: a case in
  `eval-workspace/evals/evals.json` that the current skill gets wrong and your edit gets right. The
  eval suite is the ratchet that stops improvements from regressing what already works.
- **A human approves the merge.** Drafting is automatable; merging isn't. Open a PR with explicit
  sign-off — never auto-push.
