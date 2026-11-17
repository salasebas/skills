# Performance, in order

Design for usability first and optimize after measuring. When you do:

1. `Vec::with_capacity` or `collect()` over push loops.
2. Reuse caller-owned buffers in hot APIs (`fn read_into(&mut self, buf: &mut Vec<u8>)`).
3. `Box<[T]>`, `Box<str>`, `Arc<str>` for long-lived immutable sequences; `shrink_to_fit` on long-lived collections built without a reservation.
4. A faster hasher (`foldhash`, `FxHash`) only for trusted keys.
5. Batch work instead of per-item locking.
6. Applications may set a `#[global_allocator]` such as `mimalloc`.

Derive `Copy` for small plain types and never for large ones.
