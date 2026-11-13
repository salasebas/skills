---
name: rust-development
description: "Use whenever you write, change, or review Rust code: API design, compatibility, crate features, and tests."
---

# Rust

Follow the repository's conventions, edition, toolchain, and MSRV. Keep application code direct; design library APIs around their callers and compatibility commitments.

## API decisions

- Start with a function or inherent method. Add a struct for related data or state, an enum for distinct cases, and a newtype for a meaningful distinction or validated invariant.
- Take required data in constructors. Use an options struct or builder when related optional settings make calls clearer; validate before producing a usable value. Add `Default` only for a valid, coherent default state.
- Use `Option<T>` for absence with one clear meaning. Use named methods or enums for ambiguous flags and distinct modes; clear boolean setters can stay boolean.
- Keep fields private when they protect invariants. Expose passive records deliberately: public fields, literals, and `..Default::default()` become caller contracts.
- Mark public enums expected to grow `#[non_exhaustive]` when introducing them. Keep closed logical or protocol choices exhaustive. Treat retrofitting the attribute as a source break.
- Check construction and pattern-matching compatibility before annotating structs or individual variants. Enum-level `#[non_exhaustive]` does not reserve new fields in existing variants.
- Prefer exhaustive matches where possible. Give required catch-all arms deliberate behavior; reject unknown security-sensitive choices rather than silently accepting them. `_` is not a substitute for handling known cases.
- Borrow inputs you only inspect; take ownership when you need to retain or consume them. Avoid making callers clone unnecessarily.
- Use generics for static polymorphism and `dyn Trait` for runtime heterogeneity or deliberate type erasure. Define traits for an actual extension or polymorphism boundary, not to organize methods.
- Prefer standard conversion traits and idiomatic `as_` / `to_` / `into_` methods. Return `Result` for expected failures; expose errors callers can handle and preserve their sources.
- Choose public trait implementations deliberately; `Copy`, auto traits, and `const fn` create compatibility commitments. Redact secrets from `Debug`.

## Crates and checks

- Split workspaces along real component boundaries; do not add crates speculatively. Enable only the dependency features the project needs.
- Run scoped checks for affected crates and supported feature combinations. Do not assume `--all-features` is valid when features are mutually exclusive.
- Use `cargo nextest run` for relevant tests, then `cargo test --doc`, because nextest skips doctests. Follow the repository's formatter, Clippy, and documentation checks.

## References to consult

- When designing or reviewing a public API, read the relevant [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/).
- When changing a public contract, check [Cargo's SemVer rules](https://doc.rust-lang.org/cargo/reference/semver.html). For extensibility annotations, also check the [Rust Reference](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute).
- For unresolved style or implementation choices, consult the relevant [Google Rust Style Guide](https://google.github.io/styleguide/rustguide.html) section. Apply it in context; Chromium and Fuchsia rules are not universal Cargo conventions.
