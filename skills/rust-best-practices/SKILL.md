---
name: rust-best-practices
description: "Use whenever you write, change, or review Rust code: ownership, API design, errors, crates, docs, and tests."
---

# Rust best practices

Distilled from five Rust style and design guides, with a digest of each in `references/`. Where they disagree, this file says which to follow.

The repository's conventions, edition, toolchain, and MSRV win over this file. A design record (an ADR or an architecture note) wins when it states its reason. One without a reason is an open question: report it rather than follow it. Code, rustdoc, and tests describe current behaviour, so a design record that disagrees with them is stale. A change that reverses a design record updates that record in the same change.

To review Rust code, also read [`references/review.md`](references/review.md).

## 1. Mindset

- **Write Rust-shaped code.** Model errors with `Result`, resources with ownership and `Drop`, polymorphism with traits and enums, and nullability with `Option`. Inheritance-flavored tricks (`Deref` to a "base" struct, `Manager`/`Factory` types, `throw_if_null` helpers) are smells.
- **Make invalid states unrepresentable.** Push invariants into types: enums instead of bool flags and "must be X if Y" rules, newtypes for units and IDs, fallible constructors that validate once. Then the compiler enforces the rule.
- **Application code is not library code.** Library code (anything with external users) follows the API-design rules below strictly. Application code favors simplicity and directness: concrete types, `String` or `&str` rather than `impl Into<String>` parameters, `anyhow`-style errors, `Vec` return values, no speculative generality.

## 2. Before you hand back code

Run these and fix everything they report:

```bash
cargo fmt
cargo clippy --all-targets -- -D warnings
cargo test
cargo doc --no-deps   # libraries: catches broken doc links and missing docs
```

- Check every feature combination the project supports. `--all-features` works only when features are additive; a project with mutually exclusive features names its combinations in CI.
- A project that runs `cargo nextest run` also needs `cargo test --doc`, because nextest skips doctests.
- When `cargo fmt` reformats files you did not change, revert those files.
- Fix a lint rather than silencing it. When a lint is genuinely wrong for one item, use `#[expect(clippy::name, reason = "...")]` on the narrowest item. `expect` warns when the lint stops firing, so stale suppressions get cleaned up. Use `#[allow]` only in generated code or macro output.
- Enforce warnings-as-errors in CI with `cargo clippy -- -D warnings`, never with `#![deny(warnings)]` in source: new toolchains add warnings and break the build.
- Configure lints once in `Cargo.toml` (`[lints]` or `[workspace.lints]`), not with scattered crate attributes.

## 3. Ownership and borrowing

**Prefer unique ownership.** Reach for `Rc`/`Arc` only when shared ownership is part of the design, and for `RefCell`/`Mutex` only when interior mutability is. They move checking from compile time to run time, so use them on purpose.

**Clone only data you mean to copy.** A clone that exists only to end a borrow produces a silent copy whose later changes are lost. Try these first, in roughly this order:

1. Extend a temporary with a named `let`, or shorten a borrow with a block.
2. Split a long expression into typed intermediates so the failing step is visible.
3. Move a field out of `&mut self` with `std::mem::take` (needs `Default`), `std::mem::replace`, or `Option::take` instead of cloning it.
4. Split a large struct into smaller ones so disjoint fields can be borrowed separately. The compiler tracks disjoint field borrows inside one function, but not across method calls.
5. Clone small, immutable data deliberately.
6. Use indices into an owning `Vec`, or `Rc<RefCell<_>>` with `Weak` back-pointers, as a last resort. Avoid self-referential structs.

```rust
fn a_to_b(e: &mut MyEnum) {
    if let MyEnum::A { name, x: 0 } = e {
        *e = MyEnum::B { name: std::mem::take(name) };
    }
}
```

**Accept the most general borrowed type.** `&str` not `&String`, `&[T]` not `&Vec<T>`, `&T` not `&Box<T>`, `Option<&T>` not `&Option<T>`. Deref coercion then lets callers pass owned values, borrows, or literals. Where you only read a path, string, or byte buffer, `impl AsRef<Path>` / `impl AsRef<str>` / `impl AsRef<[u8]>` is fine on parameters (never on struct fields; store `PathBuf` and `String`). Library code that only iterates takes `impl IntoIterator<Item = T>`; application code may take `&[T]`.

**Take ownership only when you need it, and then take it by value.** If a function stores or consumes its argument, take `T`, not `&T` plus an internal `.clone()`. If it only reads, take `&T`; if it mutates in place, `&mut T`. Return multiple values as a tuple or struct, not through `&mut` out-parameters (reusing a caller-owned buffer, as `Read::read` does, is the exception).

**Prefer owned data in structs.** A struct holding `&'a T` forces a lifetime onto every container. Owning a `String` or `Vec<u8>` is usually simpler and rarely the bottleneck. When a type does carry a lifetime, give it a descriptive name (`'src`, `'conn`); `'_` and `'a` are fine on simple functions.

**Freeze after setup.** Build with `let mut`, then rebind `let data = data;` so later code cannot mutate it by accident.

**Keep `Rc`, `Arc`, `Box`, and `RefCell` out of public signatures.** Take `&T`, `&mut T`, or `T` and let callers decide how to own things. A service that must be shared implements a cheap `Clone` by wrapping its state in `Arc<Inner>` internally.

## 4. Types and API design

### Naming

| Item | Case | Notes |
|---|---|---|
| Types, traits, enum variants | `UpperCamelCase` | Acronyms are one word: `Uuid`, `HttpClient` |
| Functions, methods, modules, locals | `snake_case` | |
| Constants, statics | `SCREAMING_SNAKE_CASE` | |
| Type parameters | short, from the main bound | `T`, `R: Read`, `W: Write` |
| Lifetimes | short lowercase | descriptive when on a type |

- No `get_` prefix on getters: `fn len(&self)`, `fn name(&self) -> &str`, `fn name_mut(&mut self)`. Use bare `get` only when there is one obvious thing to get (`Cell::get`). Related: `set_foo(T)`, `take_foo()`, `with_foo(|f| ..)` for closure access, and unsafe `_unchecked` siblings for checked accessors.
- Conversion prefixes signal cost and ownership: `as_` (free, borrow to borrow), `to_` (expensive, borrow to owned or borrow to borrow), `into_` (consumes `self`). Put `mut` in type order: `as_mut_slice`, not `as_slice_mut`.
- Constructors: `new` (primary), `with_capacity` / `new_with_foo` (variants), `try_new` (fallible), `from_foo` (conversion; pair important ones with a `From` impl). I/O resources use domain verbs: `File::open`, `TcpStream::connect`. An unvalidated constructor gets a name that says so, never `new`.
- `iter` / `iter_mut` / `into_iter` return types named `Iter` / `IterMut` / `IntoIter`; `keys()` returns `Keys`.
- Error types read verb-object-error: `ParseBoolError`, not `BoolParseError`.
- Name the thing a type is (`Bookings`, `Dispatcher`, `FooBuilder`) instead of a weasel suffix such as `Service`, `Manager`, `Factory`, `Helper`, or `Util`. Leave the module name out of the type (`foo::Id`, not `foo::FooId`). Avoid abbreviations an outsider wouldn't know.
- If you implement `len()`, implement `is_empty()`.
- Feature names are bare: `std`, `serde`, `alloc`, never `use-std` or `no-std`.

### Model the domain with types

- **Newtypes** for semantic distinctions: `struct Miles(f64)` and `struct Kilometers(f64)` cannot be mixed, where a type alias can. Add `#[repr(transparent)]` when layout matters, and derive or forward the traits you need. A newtype that encodes an invariant (`Month`) validates in a fallible constructor (`TryFrom`, `FromStr`, `try_new`) and never offers an infallible `From` from the raw type.
- **Enums or named methods instead of `bool` parameters in public or shared signatures.** `report(true)` is unreadable at the call site and cannot grow a third mode. Use a two-variant enum (`Verbosity::Summary`, `Verbosity::Full`) or two methods (`report()`, `report_verbose()`): `Widget::new(Size::Small, Shape::Round)`, not `Widget::new(true, false)`. A private helper whose call sites sit a few lines away may keep its `bool`.
- **Named fields over tuples**, except single-field newtypes and very local code.
- **`Option` for absence, never sentinels** such as `-1` or `""`. **Data-carrying enums** instead of "field X is only meaningful when Y is set".
- **Use the strongest std type:** `PathBuf` / `&Path` for paths, `Duration` for spans, `NonZeroU32` internally only (keep plain integers at API boundaries).
- **Independent flags** use the `bitflags` crate; an enum models exactly one choice.

### Derive and implement the standard traits eagerly

Downstream crates cannot add std traits to your types (orphan rule), so you must. Derive whenever every field supports it: `Debug` (on every public type; hand-write it to redact secrets), `Clone` (except unique resources and key material), `Copy` (only small bitwise-copyable types, because the compiler copies silently), `PartialEq` / `Eq`, `PartialOrd` / `Ord` (never ship `PartialOrd` without `Ord` when a total order exists), `Hash` (consistent with `Eq`), and `Default` when an obvious neutral value exists. Implement `Display` for anything meant to be read: error types, string-like wrappers. Add `#[must_use]` to pure functions and to types, such as errors and lazy values, whose discarding is a bug.

Implement `From` / `TryFrom`, never `Into` / `TryInto` directly (blanket impls give you those). Prefer `from` / `into` over `as`, which silently allows lossy casts. Implement `FromStr` rather than an ad-hoc `from_str` method, `FromIterator` and `Extend` on collections, and `IntoIterator` for both owned and borrowed forms. Implement `Deref` only on smart pointers and owning collections (`Vec<T>` to `[T]`), never to fake inheritance. Overload operators only for their mathematical meaning.

Put trait bounds on the `impl` blocks that need them, not on struct definitions: `#[derive(Clone)] struct Good<T>`, not `struct Bad<T: Clone + Debug>`.

If you hand-write `Ord`, hand-write `PartialEq`, `PartialOrd`, and `Hash` to agree with it (compare the same fields, ignore the same fields). A derived `PartialEq` next to a custom `Ord` breaks the std contract and misbehaves in `BTreeMap` and `sort`/`dedup`. Say in the docs which fields equality ignores.

### Constructors, builders, defaults

- Provide `new()` even when `Default` exists, and make them agree (one delegates to the other). Derive or implement `Default` so callers can write `..Default::default()`; bag-of-options structs with public fields always have it.
- When the caller must make a choice that has no safe default, such as a trust or security policy, take an enum with data-carrying variants and no `Default`, and give the unsafe variant a name that says so. A `Default` there picks the policy for every caller who never read the docs.
- Up to two optional parameters: inherent constructors (`new`, `with_a`, `with_b`). Beyond that, or when construction validates or has side effects, add a builder: `Foo::builder()` returns `FooBuilder`, setters are named after fields (`timeout(d)`, not `set_timeout`) and infallible, and `build() -> Result<Foo, Error>` does all validation including cross-field checks. Prefer non-consuming setters (`&mut self -> &mut Self`) unless `build` must move a value out.
- A constructor with four or more loose arguments groups them into semantic types: `Deposit::new(account, amount)` rather than four `&str` / `u64` parameters.

### Visibility and evolution

- Private by default. Fields stay private unless the struct is passive C-style data. Widen to `pub(crate)` or `pub(super)` before `pub`. Making an item more public later is non-breaking; the reverse is breaking, and every `pub` item is a promise. Public fields, `Copy`, auto traits, `const fn`, and every `#[doc(hidden)] pub` item are such promises too.
- Mark a new public enum or public-field struct that crosses crate boundaries `#[non_exhaustive]` when you introduce it, unless the set is a stable ontology. Adding the attribute to an existing public type, or to an options struct callers build with `..Default::default()`, is a breaking change.
- In a `match` on your own enums, list every variant. Keep a `_` arm only for a foreign `#[non_exhaustive]` enum, after the variants you handle.
- Seal traits you don't want implemented downstream, and say so in the docs:

  ```rust
  pub trait TheTrait: private::Sealed { /* ... */ }
  mod private {
      pub trait Sealed {}
      impl Sealed for usize {}
  }
  ```

- Library code returns iterators, not a `Vec` collected only to return, behind `impl Iterator<Item = T>` (internal APIs) or a newtype (public APIs you must keep stable).
- Expose each public item at exactly one path. `pub use` a foreign crate's items only in an umbrella crate. Keep third-party types out of your public API; feature-gate `serde` impls behind a feature named `serde`. If a dependency's type must appear, re-export it so callers can name the matching version.
- Mark a function `const` only if it will stay `const`. Keep `ErrorKind` enums and other internals private when they would lock in failure modes you consider private.

### Traits and generics

- Define a trait only for generic programming (`T: Trait`, `impl Trait`, `dyn Trait`) or as an extension trait (`FooExt`), never only to organize code. Put essential functionality in inherent methods and have trait impls forward to them, so callers need no import.
- Prefer, in order: concrete types; generics (`T: Trait`, `impl Trait`); `dyn Trait`, ideally wrapped in your own struct (`struct DynStore(Arc<dyn Store>)`). Generics give static dispatch and inlining; trait objects give heterogeneous collections and smaller binaries. Keep generics on service-level types one level deep (`Service<Backend>`, not `Service<Backend<Store>>`).
- Decide early whether a trait must be object-safe. Generic methods or `Self` outside the receiver break it; exclude such methods with `where Self: Sized`.
- Keep required trait methods minimal and provide defaults for everything derivable from them, as `Iterator` does from `next`.
- If a function has a clear receiver, make it a method. A computation with no receiver is a free function, not `Database::check(params)`. Associated functions are for construction.
- Closures: use the most general bound that works (`FnOnce` if called once, `FnMut` if it mutates, else `Fn`) and prefer `Fn*` bounds to bare `fn` pointers. Closure parameters go last, one per function.
- Keep parameter order consistent across a crate: call-specific first, ubiquitous context (loggers, allocators) last.
- Reach for a macro only when functions, generics, and traits cannot do the job. Prefer `macro_rules!` to proc macros, make macro input look like the output it generates, and keep a type's kind and a function's signature as written.

### Refactoring someone else's code

- Fix every smell the request is about, not just the cheap ones: clones that only satisfy the borrow checker, `&String` / `&Vec<T>` parameters, `unwrap` on fallible paths, `Rc<RefCell<_>>` in signatures, `get_` getters, `bool` parameters, `+` string concatenation, `#![deny(warnings)]`, error types without `Error`, nondeterministic `HashMap` iteration in output.
- Keep public behavior identical unless changing it is the point: the same operations, the same success and failure semantics, the same output bytes. Turning a panic into an `Err` is the change callers want. Dropping an error variant, removing a derive, or changing what a constructor takes is not; if a signature must change, show the before and after in the change list and say why.
- Preserve quirks you don't understand and flag them, rather than silently "fixing" them.
- When the module has no tests, pin the current behavior with a few before you touch it.

## 5. Errors and panics

Pick the mechanism by contract:

| Situation | Use |
|---|---|
| Absence is normal (`first()`, `checked_add`) | `Option<T>` |
| The caller may need to know what went wrong | `Result<T, E>` |
| A bug or violated invariant inside your code | `panic!` / `assert!` / `expect("why")` |

**Panics are not exceptions.** A panic means "stop now". Report bad input with `Result`. A library lets panics propagate: `catch_unwind` does nothing under `panic = "abort"` and can leave state inconsistent. Where a panicking convenience is justified, pair it with a fallible API (`v[i]` / `v.get(i)`, `new` / `try_new`) and document it under `# Panics`.

**Every intentional panic carries a message with the relevant values:** `assert!(buf.len() >= HEADER, "buffer too small: {} bytes", buf.len())`, `expect("config should be loaded before workers start")`. Prefer `expect("reason")` to `unwrap()`. Phrase the `expect` message as the expectation that failed, not a restatement of the condition.

**Pattern-match instead of check-then-unwrap:** `if let Some(v) = opt { .. }` or `let Some(v) = opt else { return .. };`, never `if opt.is_some() { opt.unwrap() }`.

**Lock poisoning is fatal:** `.lock().expect("lock poisoned")`. Don't recover with `into_inner`.

**A function that verifies or checks returns `Err` when the check fails**, so `check(..)?` stops the caller. A `bool` result lets the caller forget to look.

**Library error types** (any `E` in a public `Result`):

- Implement `std::error::Error` (which requires `Debug` + `Display`), be `Send + Sync + 'static`, and implement `source()` for wrapped causes. A library's public error type is never `()`, `String`, or `Box<dyn Error>`.
- `Display` messages are lowercase, concise, and have no trailing punctuation: `"invalid header length"`.
- Implement `From<Upstream>` so `?` converts. Use `map_err` only for foreign errors or to add context.
- Two sound shapes: an enum with one variant per cause (`thiserror` generates this well), or a struct with a private `kind` plus `is_xxx()` and accessor methods, as `std::io::Error` does. Prefer an error per operation when callers handle each operation's failures differently. Expose only details callers can act on.
- If a fallible function consumes an argument, return it inside the error so the caller can retry without cloning (`FromUtf8Error::into_bytes`).
- Keep `anyhow::Error` out of a library's public API.

**Application error handling:** `anyhow` or `eyre` with `.context("opening config")` is the right tool. Use one app-level error type, not several. `main` may return `Result<(), anyhow::Error>`.

**Destructors never fail, panic, or block.** Provide `close(self) -> Result<()>` for fallible teardown and let `Drop` do best-effort cleanup.

**Document failure modes:** `# Errors` for any `Result`, `# Panics` for any reachable panic, `# Safety` for every `unsafe fn`.

## 6. Everyday idioms

- **Iterators over hand loops** when the pipeline is short and reads top-down: `values.iter().filter(..).map(..).collect()`, `.any()`, `.sum()`, `.fold()`. Collect fallible steps into `Result<Vec<_>, E>` and apply `?`. Keep an explicit `for` loop when the body is large, does several jobs, or needs awkward early returns. Bind a long chain to a named variable rather than putting it in a `for` header, and prefer `for x in it` to `.for_each(|x| ..)`.
- **`Option` / `Result` combinators** (`map`, `and_then`, `ok_or_else`, `unwrap_or_else`, `as_ref`, `as_deref`) when they're clearer than `match`, and `match` when they're not.
- **`format!` / `write!`** with inline args (`format!("{name}: {count}")`) for concatenation and substitution, not chained `+` or `str::replace`. `write!` into an existing buffer in hot paths.
- **Explicit types where inference obscures intent:** on `.into()`, `.parse()`, `.collect()`, and complex iterator results. Prefer `let x: Vec<u32> = ..` to a turbofish.
- **Drop guards for cleanup** that must run on early return or unwind. Bind them to a name (`let _guard = ..`), because `let _ = ..` drops immediately.
- **Closures that capture mixed ownership:** rebind in a block, then `move`:

  ```rust
  let job = {
      let cfg = cfg.clone();
      move || run(cfg, data)
  };
  ```

- **Import style:** one `use` per module path (`use foo::bar::{Bar, Baz};`); types and traits imported and used unqualified (`Regex`); free functions qualified by their module (`mem::take`, `fs::read`). Import a trait inside the function that needs it unless the whole file uses it. Globs only for `use super::*` in tests, `use Enum::*` in a function that matches on it, and a framework's documented prelude.
- **Magic numbers** become named `const`s.
- **Logging:** structured events through `tracing` or `log`, not `println!` / `dbg!`, except for a CLI's own stdout output.

## 7. Crates, modules, dependencies

- **Prefer small, single-purpose crates** split along real component boundaries, in a flat `crates/` workspace; keep each crate out of another crate's `src/`. Split when a crate grows a second purpose. Share versions and lints through `[workspace.dependencies]` and `[workspace.lints]`.
- **Modules:** name a leaf module after its primary item (`Foo` lives in `foo.rs`). Non-leaf modules contain only `mod` declarations and re-exports. Put the essential items at the crate root and group the rest by use case (`account`, `network`), not by kind (`traits`, `errors`). Don't define a prelude.
- **Re-export individually** (`pub use foo::{A, B};`), never with a glob.
- **Dependencies:** every one costs compile time, binary size, and supply-chain exposure, including `build.rs` and proc macros. Enable only the dependency features the project needs. Use ranges (`"1"`, `"1.4"`), never `"*"` or a needless `"="`. Commit `Cargo.lock` for binaries. Audit with `cargo tree --duplicates`, `cargo deny`, `cargo udeps`, and `cargo audit`.
- **Features are additive and bare-named:** `std`, `serde`, `alloc`, `test-util`. A feature adds public items; it never removes or changes one, and it never gates a struct field or a trait method. Put mocks and fakes behind `test-util`.
- **Semver:** breaking changes include removing or renaming public items, adding a variant to an enum that isn't `#[non_exhaustive]`, adding a field to a publicly constructible struct, adding a trait bound, or making a trait non-object-safe. Deprecate in a minor release before removing in a major one. Use the latest stable edition for new crates and set an MSRV deliberately. The [Cargo SemVer reference](https://doc.rust-lang.org/cargo/reference/semver.html) lists every case.
- Run code only from `main()` onward (no `ctor`-style crates). Use unstable features only on a nightly toolchain.

## 8. Documentation

- `///` on every public item; `//!` at the top of every public module and the crate root. The first sentence is a single line of about fifteen words, because it becomes the summary in listings.
- Sections, in this order, as applicable: `# Examples`, `# Errors`, `# Panics`, `# Safety`. Examples use `?` with the `fn main` hidden behind `# ` lines, never `unwrap()`, because users copy them verbatim. Describe parameters in prose, not a table.
- Document what the signature can't say: preconditions, side effects, ownership transfer, and complexity. `/// Removes an element.` on `remove_element` restates the name and adds nothing.
- Link items with `` [`Type`] ``. Hide impls users never trigger (`From<PrivateError> for PublicError`) with `#[doc(hidden)]`.

## 9. Tests

- Unit tests in `#[cfg(test)] mod tests { use super::*; .. }` for private internals. Integration tests in `tests/` for anything reachable through the public API, and prefer that location when either would do. Doc examples are tests too.
- Cover each feature combination and each platform-specific path.
- Anything doing I/O, time, randomness, or network must be mockable: `new_mocked() -> (Self, MockCtrl)` behind `test-util`, not a `Default` that performs I/O.
- Fuzz parsers of untrusted input with `cargo fuzz`. Benchmark with `criterion` or `divan` and `std::hint::black_box`. Run Miri over `unsafe`.
- Assertions get context so failures read well: `assert_eq!(got, want, "input {input:?}")`.

## References

Read the one that matches the task. The first three cover code most crates do not have; the rest are digests of one source each, for the reasoning behind a rule or a complete checklist.

- [`references/review.md`](references/review.md): reviewing Rust code; what to look for, in priority order.
- [`references/concurrency-and-async.md`](references/concurrency-and-async.md): threads, locks, channels, `async`, or `Send` bounds.
- [`references/unsafe-and-ffi.md`](references/unsafe-and-ffi.md): `unsafe`, FFI, or `-sys` crates.
- [`references/performance.md`](references/performance.md): optimizing after a measurement.
- [`references/rust-api-guidelines.md`](references/rust-api-guidelines.md) (https://rust-lang.github.io/api-guidelines/): designing a public API or crate; all 54 checklist items with conventions.
- [`references/effective-rust.md`](references/effective-rust.md) (https://www.lurklurk.org/effective-rust/): choosing between alternatives: generics vs `dyn`, `Result` vs panic, iterators vs loops, borrow-checker tactics, dependencies, CI.
- [`references/rust-design-patterns.md`](references/rust-design-patterns.md) (https://rust-unofficial.github.io/patterns/): idioms, patterns, and anti-patterns with code.
- [`references/microsoft-rust-guidelines.md`](references/microsoft-rust-guidelines.md) (https://microsoft.github.io/rust-guidelines/): error struct design, panic policy, unsafe policy, async, workspace layout, performance.
- [`references/google-rust-style-guide.md`](references/google-rust-style-guide.md) (https://google.github.io/styleguide/rustguide.html): formatting, imports, module layout, accessor naming, application vs library.
