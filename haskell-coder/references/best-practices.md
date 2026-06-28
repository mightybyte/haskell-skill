# Best Practices

## Code Organization

### Keep Modules Focused
- One concern per module. If a module grows past ~300 lines, split it.
- **Import whole modules, not individual symbols** (e.g. `import Control.Monad.Reader`, not `import Control.Monad.Reader (asks, runReaderT)`). This keeps diffs small when symbols are added/removed/renamed, avoids the import list rotting out of sync with usage, and saves an edit round-trip on every call-site change. Use explicit import lists only when there's a concrete reason — name clashes, `qualified` aliases, or a Prelude replacement under `NoImplicitPrelude`.
- Types go in their own module to break import cycles.
- `Internal/` modules are implementation details — no stability guarantees.

### Avoid Circular Imports
If module A imports B and B imports A:
1. Extract shared types into a `Types` module that both import.
2. Use `hs-boot` files only as a last resort.

## Haddock Documentation

### Module Headers
```haskell
-- |
-- Module : MyProject.DB
-- Description : Database access layer
-- Copyright : (c) Your Name, 2024
-- License : MIT
-- Maintainer : you@example.com
--
-- Functions for querying and updating the database.
-- All operations run in the 'App' monad and use connection pooling.
module MyProject.DB
  ( -- * Queries
    getUser
  , getUserByEmail
    -- * Mutations
  , saveUser
  , deleteUser
  ) where
```

### Function Documentation
```haskell
-- | Fetch a user by their unique identifier.
--
-- Returns 'Nothing' if no user exists with the given 'UserId'.
--
-- ==== Examples
--
-- >>> runApp env $ getUser (UserId 42)
-- Just (User {userName = "alice", userEmail = "alice@example.com"})
--
-- >>> runApp env $ getUser (UserId 999)
-- Nothing
getUser :: UserId -> App (Maybe User)

-- | Save a user to the database.
--
-- * Inserts if the user does not exist.
-- * Updates if a user with the same 'UserId' already exists.
--
-- Throws 'DatabaseException' on connection failure.
saveUser :: User -> App ()
```

### Data Type Documentation
```haskell
-- | Application configuration loaded from @config.yaml@.
data AppConfig = AppConfig
  { configHost :: !Text
    -- ^ Hostname to bind the server to (e.g. @"0.0.0.0"@).
  , configPort :: !Int
    -- ^ Port number. Defaults to @8080@.
  , configDbUrl :: !Text
    -- ^ PostgreSQL connection string.
  } deriving stock (Show, Eq, Generic)
    deriving anyclass (FromJSON)
```

### Building Haddock
```bash
# Local docs
cabal haddock

# With cross-references to dependencies
cabal haddock --haddock-all

# Open in browser
cabal haddock --open
```

### Haddock Markup Quick Reference
| Syntax | Meaning |
|--------|---------|
| `-- \|` | Documentation for the next declaration |
| `-- ^` | Documentation for the preceding field/argument |
| `'TypeName'` | Link to a type or function |
| `@code@` | Inline code |
| `> expression` | Code block (must be indented) |
| `==== Heading` | Section heading inside a doc comment |
| `* item` | Bulleted list |
| `\<url\>` | Hyperlink |
| `/emphasis/` | Emphasis |

## Style Guide

### Naming Conventions
```haskell
-- Types and constructors: PascalCase
data UserRole = Admin | Editor | Viewer

-- Functions and variables: camelCase
getUserRole :: UserId -> App UserRole

-- Type variables: short lowercase
mapMaybe :: (a -> Maybe b) -> [a] -> [b]

-- Modules: PascalCase with dots
module MyProject.Auth.Token where

-- Constants: camelCase (no ALL_CAPS)
maxRetries :: Int
maxRetries = 3

-- Record fields: prefixed with underscore and type name
data Config = Config
  { _config_host :: !Text
  , _config_port :: !Int
  }
```

### Formatting

```haskell
-- Use where clauses for local definitions
processOrder :: Order -> App Receipt
processOrder order = do
  validated <- validate order
  receipt   <- charge validated
  notify receipt
  pure receipt
  where
    validate o = ...
    charge v = ...
    notify r = ...

-- Pattern match on the left when possible
fib 0 = 0
fib 1 = 1
fib n = fib (n-1) + fib (n-2)

-- Use guards for conditional logic
classify :: Int -> Text
classify n
  | n < 0 = "negative"
  | n == 0 = "zero"
  | otherwise = "positive"
```

### General Style Rules
- Prefer `where` over `let` for multi-line local definitions.
- Avoid point-free style when it hurts readability (i.e. most of the time): `f x = g (h x)` is clearer than `f = g . h` when the pipeline is complex.
- Use blank lines to separate logical sections within a module.
- Parenthesise `$` only when nesting; prefer `$` for single-application chains.

## CI Best Practices

### Recommended CI Checks
A good Haskell CI pipeline runs these steps (see `references/cabal-guide.md` for full GitHub Actions examples):

1. **Build** — `cabal build` with `-Werror` to catch warnings.
2. **Test** — `cabal test --test-show-details=direct`.
3. **Lint** — `hlint src/` for style issues.
5. **Documentation** — `cabal haddock` to catch broken doc references.

### GHC Version Matrix
Test against the GHC versions you support:
```yaml
strategy:
  matrix:
    ghc: ['9.4', '9.6', '9.8', '9.10', '9.12']
```

For libraries, test a range. For applications, testing the single target GHC is usually sufficient.

### Dependency Caching
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cabal/store
      dist-newstyle
    key: ${{ runner.os }}-ghc-${{ matrix.ghc }}-${{ hashFiles('**/*.cabal', 'cabal.project') }}
    restore-keys: |
      ${{ runner.os }}-ghc-${{ matrix.ghc }}-
```

Cache both the cabal store and `dist-newstyle` for faster incremental builds.

## General Best Practices

### Write Total Functions
```haskell
-- BAD: partial — crashes on empty list
firstElement :: [a] -> a
firstElement xs = head xs

-- GOOD: total — type encodes possibility of failure
firstElement :: [a] -> Maybe a
firstElement []    = Nothing
firstElement (x:_) = Just x
```

### Make Dependencies Explicit
```haskell
-- BAD: hidden dependency on global state
getConfig :: IO Config
getConfig = readIORef globalConfigRef

-- GOOD: explicit dependency via argument or Reader
getConfig :: MonadReader AppEnv m => m Config
getConfig = asks appConfig
```

### Separate Pure and Effectful Code
```haskell
-- BAD: IO mixed into business logic
processOrder :: Order -> IO Receipt
processOrder order = do
  let total = sum (map itemPrice (orderItems order))
  let tax = total * 0.1
  now <- getCurrentTime
  writeToDb (Receipt total tax now)
  pure (Receipt total tax now)

-- GOOD: pure calculation separated from effects
calculateReceipt :: UTCTime -> Order -> Receipt
calculateReceipt now order = Receipt total tax now
  where
    total = sum (map itemPrice (orderItems order))
    tax   = total * 0.1

processOrder :: Order -> App Receipt
processOrder order = do
  now     <- liftIO getCurrentTime
  let receipt = calculateReceipt now order
  saveReceipt receipt
  pure receipt
```

### Use Newtypes at Boundaries
```haskell
-- Wrap external/serialized data in newtypes at the boundary
newtype RawJson = RawJson { unRawJson :: ByteString }
newtype Validated a = Validated { unValidated :: a }

parseAndValidate :: RawJson -> Either AppError (Validated Order)
```

### Keep `main` Thin
```haskell
-- app/Main.hs
module Main (main) where

import MyProject

main :: IO ()
main = do
  config <- defaultConfig
  runApp config
```

All logic lives in the library. The executable is a thin wrapper. This makes everything testable without running the executable.
