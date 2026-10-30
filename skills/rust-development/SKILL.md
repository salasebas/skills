---
name: rust-development
description: "Use whenever you write or change Rust code: workspaces, crate features, public APIs."
---

# Rust

- Use the latest Rust and Cargo versions and features to ensure optimal performance
- Consider using rust workspaces and divide the project into distinct internal crates to reduce build times
- Avoid exposing generics via public or inter-crate APIs (unless there is a really good reason)
- Only activate required features on external crates
