# C and C++ boundaries

Read when translating C or C++ representations and lifetime rules.

- `char *` is not a promise of UTF-8. Determine whether the API carries arbitrary bytes, a null-terminated string, a platform encoding, or an explicit-length sequence. Use byte slices/owned bytes when appropriate; validate or decode before constructing Rust text. Embedded NUL and non-UTF-8 data may be valid for length-delimited inputs.
- Map owned allocations and handles to owned Rust values and RAII wrappers. Establish who allocates, aliases, mutates, and frees each resource, including early-return paths. Do not mechanically map every pointer to `Box` or give borrowed storage an owning destructor.
- Represent optional values with `Option` and expected errors with useful `Result` types. Keep distinct error codes and payloads when callers distinguish them. Move out-parameter values into returns while preserving partial-result/error semantics.
- A fixed-size buffer may impose observable truncation, accepted-size, or failure behaviour. Removing the limit can change the contract; agree on that change rather than assuming growable storage is equivalent. Likewise, check locale-sensitive comparisons, integer widths, signedness, overflow, and parser acceptance rules against the original.
- Choose typed flags or options when they clarify legal states. If unknown bits or bit-exact protocol values are supported, preserve their representation and round trips rather than rejecting them implicitly.
- Preserve C++ copying/moving, iterator invalidation, destruction order, and exception-to-error behaviour where callers depend on them. Do not port class hierarchies literally when composition or an enum satisfies the same contract.
- Preserve an ABI only when required. Then validate calling convention, layout, ownership transfer, nullability, unwind boundaries, and allocator pairing; ordinary Rust structs and strings are not automatically FFI-compatible. Do not mirror source undefined behaviour in a safe Rust API.

Primary reference: [Rustonomicon FFI](https://doc.rust-lang.org/nomicon/ffi.html).
