---
name: rust-development
description: "Use whenever you write, change, or review Rust code."
---

# Rust

Follow the repository's conventions, edition, toolchain, and MSRV. Before changing a public API, read the repository's design records (ADRs, architecture docs, migration guides); a change that reverses one updates that record in the same change. For everything this file does not decide, follow the [Rust API Guidelines][guidelines].

## API choices

- Application code stays direct: concrete types instead of speculative generics or `impl Into<T>`, `&str` and `&[T]` parameters, `Vec` returns. The library rules apply to crates with external callers.
- Give each value one construction path and one validation point: required data in the constructor or `builder(required)`, validation in `try_new` or `build`, private fields behind it. An unvalidated constructor gets a name that says so, never `new`. ([C-CTOR], [C-BUILDER], [C-STRUCT-PRIVATE])
- Name constructors after the mode they create (`StartSso::redirect()`) instead of taking a `bool` or a mode argument. A `bool` whose meaning is clear at the call site can stay. ([C-CUSTOM-TYPE])
- When the caller must make a choice with no safe default, such as a trust or security policy, take an enum with data-carrying variants and no `Default`, and give the unsafe variant a name that says so.
- A function that verifies or checks returns `Err` when the check fails, so `check(..)?` stops the caller. ([C-GOOD-ERR])
- List the variants in a `match` on your own enums; keep a `_` arm for a foreign `#[non_exhaustive]` enum.
- Mark a new public enum that is expected to grow `#[non_exhaustive]` when you introduce it, and keep closed choices exhaustive. Adding the attribute to an existing public type, or to an options struct callers build with `..Default::default()`, is a source break. ([SemVer: non_exhaustive][semver-ne])
- Pick generics or `dyn Trait` for the boundary at hand. ([Effective Rust 12][er-generics])
- Public fields, `Copy`, auto traits, `const fn`, and every `#[doc(hidden)] pub` item are compatibility commitments: add them on purpose and keep the rest crate-private. ([Effective Rust 22][er-visibility], [SemVer][semver])

## Crates and checks

- Split crates along real component boundaries. Enable only the dependency features the project needs.
- Check the affected crates with the feature combinations the project supports; `--all-features` is invalid when features are mutually exclusive.
- Run `cargo nextest run`, then `cargo test --doc`, because nextest skips doctests.

[guidelines]: https://rust-lang.github.io/api-guidelines/
[C-CTOR]: https://rust-lang.github.io/api-guidelines/predictability.html#c-ctor
[C-BUILDER]: https://rust-lang.github.io/api-guidelines/type-safety.html#c-builder
[C-STRUCT-PRIVATE]: https://rust-lang.github.io/api-guidelines/future-proofing.html#c-struct-private
[C-CUSTOM-TYPE]: https://rust-lang.github.io/api-guidelines/type-safety.html#c-custom-type
[C-GOOD-ERR]: https://rust-lang.github.io/api-guidelines/interoperability.html#c-good-err
[semver]: https://doc.rust-lang.org/cargo/reference/semver.html
[semver-ne]: https://doc.rust-lang.org/cargo/reference/semver.html#attr-adding-non-exhaustive
[er-generics]: https://effective-rust.com/generics.html
[er-visibility]: https://effective-rust.com/visibility.html
