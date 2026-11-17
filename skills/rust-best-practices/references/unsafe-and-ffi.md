# Unsafe and FFI

- Write `unsafe` only for one of three reasons: a novel abstraction safe code can't express, a benchmarked performance need, or FFI and platform calls. Reach for std and well-reviewed crates first; they already contain the audited `unsafe`.
- Every `unsafe` block or impl gets a `// SAFETY:` comment stating why the invariants hold. Every `unsafe fn` gets a `# Safety` doc section listing what the caller must uphold. Enable `unsafe_op_in_unsafe_fn`.
- Keep `unsafe` in the smallest module that can uphold its invariant and wrap it in a safe API; the module boundary is the soundness boundary. A safe function that can cause undefined behavior through any sequence of safe calls is unsound, and unsound code is never acceptable.
- Mark a function `unsafe` only when misuse can cause undefined behavior, not because it is dangerous (`delete_database()` is a safe function).
- Cast enums with `TryFrom` or a `match`, and fix lifetimes in the types, instead of `transmute`. Make a type `Send` by fixing its fields, instead of `unsafe impl Send`.
- Test unsafe code under Miri and with adversarial inputs.
- FFI: `#[repr(C)]` on shared structs, sized integer types, `CString` / `CStr` for strings, allocate and free on the same side, wrap C-owned pointers in an RAII type whose `Drop` frees them, check for null and return `Result`, and stop panics at the boundary with `catch_unwind`. Generate bindings with `bindgen` in a `foo-sys` crate and keep business logic in a safe core crate.
