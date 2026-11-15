---
name: rust-development
description: "Use whenever you write, change, or review Rust code: API design, compatibility, crate features, and tests."
---

# Rust

Follow the repository's conventions, edition, toolchain, and MSRV. For public API design, follow the Rust API Guidelines; this file records only the choices I want made a specific way.

## API choices

- Application code stays direct: concrete types, `&str` and `&[T]` parameters, `Vec` returns, no speculative generics or `impl Into<T>`. The library rules apply to crates with external callers.
- Give each value one construction path and one validation point. Take required data in the constructor or `builder(required)`, and validate in `try_new` or `build`. Don't also offer public fields, an unvalidated `new`, and a separate `validate()` for the same type.
- Name constructors after the mode they create (`StartSso::redirect()`), not a `bool` or a mode argument. A `bool` whose meaning is clear at the call site can stay `bool`.
- When the caller must make a choice that has no safe default, such as a trust or security policy, take an enum with data-carrying variants and no `Default`. Give the unsafe variant a name that says so.
- Add `#[non_exhaustive]` to a new public enum expected to grow. Keep closed choices exhaustive. Don't retrofit it onto existing public types (a source break), or onto options structs that callers build with `..Default::default()`.
- Pick generics or `dyn Trait` for the boundary at hand, with no blanket rule.
- Public fields, `Copy`, auto traits, and `const fn` are compatibility commitments, and so is a `#[doc(hidden)] pub` item. Add them on purpose.

## Crates and checks

- Split crates along real component boundaries only. Enable only the dependency features the project needs.
- Check the affected crates with the feature combinations the project supports. `--all-features` is invalid when features are mutually exclusive.
- Run `cargo nextest run`, then `cargo test --doc`, because nextest skips doctests.

## References

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/): designing or reviewing a public API.
- [Cargo SemVer](https://doc.rust-lang.org/cargo/reference/semver.html): changing a public contract, including adding `#[non_exhaustive]`, fields, variants, or trait bounds.
- [Effective Rust](https://effective-rust.com/): choosing between alternatives, such as generics or `dyn Trait`, `Result` or panic, and builder or constructor.
