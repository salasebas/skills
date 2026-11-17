# Reviewing Rust code

Work through these in order. The first two categories are where real bugs live. Cite the rule behind each finding so a reader can look it up: an API Guidelines code such as `C-GETTER`, an Effective Rust item number, a Microsoft guideline code such as `M-PANIC-ON-BUG`, a clippy lint name, or "Google Rust Style Guide".

Hold library code (a `lib.rs`, `pub` items used by other crates, a published `Cargo.toml`) to the API-design rules strictly. Hold application code to the simplicity rules instead: concrete types, `anyhow`-style errors, and no speculative generality. Check the edition and MSRV in `Cargo.toml` before recommending a newer feature.

## Correctness and soundness

- Undefined behavior: an `unsafe` block without a `// SAFETY:` comment, `transmute` to cast enums or extend lifetimes, `unsafe impl Send`/`Sync` used to silence the compiler, or a safe function that can cause UB through safe calls (unsound).
- Panics on reachable paths: `unwrap()`, `expect()`, indexing, `as` casts that wrap, or integer overflow, wherever input from outside can reach them.
- Trait contracts: a hand-written `Ord` with a derived `PartialEq`, or `Hash` that disagrees with `Eq`. These silently corrupt `BTreeMap`, `HashMap`, `sort`, and `dedup`.
- Lock hazards: a `MutexGuard` held across `.await` or returned to a caller, user closures called under a lock, or a poisoned lock recovered with `into_inner`.
- Destructors that panic, block, or can fail.

## Error handling

- Errors that callers can't use: `()`, `String`, or `Box<dyn Error>` as a library's public error type, an error enum without `Display` and `std::error::Error`, or `anyhow::Error` in a library's public API.
- Errors that lose information: `map_err(|_| ...)`, no `source()`, or messages without the path, line, or value that failed.
- A check that returns `bool` where a failed check should be an `Err`.
- Panics used for expected failures, or `catch_unwind` used as control flow.

## API design (strict for libraries)

- Parameters: `&String`, `&Vec<T>`, or `&Box<T>` instead of `&str`, `&[T]`, or `&T`; a `bool` parameter in a public signature; ownership taken and then cloned, or a borrow cloned internally to get ownership; `impl Into<T>` in application code, or on a library function too rarely called to justify a copy per argument type.
- Return types: a library function that collects into a `Vec` only to return it, when an iterator would do. Owned results are fine when callers need ownership or random access, or when building the collection is the function's job.
- Visibility: public fields that should be private, `Rc`, `RefCell`, or `Arc` in public signatures, or third-party types leaking into the API.
- Missing standard traits: `Debug` on public types, `Display` on errors, `Default` next to a zero-argument `new()`, and `FromStr` instead of an ad-hoc `from_str` method. A `Default` on a choice with no safe default, such as a security policy, is the opposite finding.
- Naming: `get_` prefixes on getters, `as_`/`to_`/`into_` that don't match their cost and ownership, and `Manager`/`Service`/`Util` names.
- Evolution: new public enums or structs that should be `#[non_exhaustive]`, the attribute added to an existing public type (a breaking change), or traits that should be sealed.

## Idiom and clarity

- Clones that exist only to satisfy the borrow checker.
- Check-then-unwrap (`if x.is_some() { x.unwrap() }`), and `match` where a combinator is clearer, or the reverse.
- String building with `+`, hand loops that are clearer as iterators, or iterator chains long enough to need a loop.
- `HashMap` iteration order leaking into output or tests.
- `#![deny(warnings)]` in source, `#[allow]` without a reason, and glob imports of external crates (a framework's documented prelude is fine).

## Documentation and tests

- Public items without docs, and docs that restate the name.
- Missing `# Errors`, `# Panics`, or `# Safety` sections where they apply.
- Doc examples that use `unwrap()` instead of `?`.
- Logic with no tests.
