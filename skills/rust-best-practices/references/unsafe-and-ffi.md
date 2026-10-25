# Unsafe and FFI decisions

Read before changing unsafe operations, foreign interfaces, or safe wrappers around them.

- State why safe facilities cannot satisfy the requirement. Prefer a narrow audited boundary over spreading unsafe operations through callers.
- Trace allocation provenance, validity, alignment, initialisation, aliasing, lifetimes, thread access, and destruction for every affected pointer or reference. Validate lengths and arithmetic before constructing views. Include zero-sized and empty cases where relevant.
- Document each unsafe operation's proof obligations with a specific `SAFETY` explanation and each unsafe API's caller obligations. A missing comment is a reviewability gap, not itself proof of undefined behaviour; an existing comment is not proof of correctness.
- A safe wrapper must uphold its invariants for every permitted safe call sequence, including failures and destruction. Review construction, mutation, callbacks, concurrency, and reentrancy together. Do not use `transmute` or unsafe `Send`/`Sync` implementations to bypass unresolved invariants; legitimate uses require an actual proof.
- Match the declared ABI and representation. Check layout, integer widths, nullability, string termination/encoding, ownership transfer, allocator pairing, and callback lifetime. `repr(C)` alone does not make a type or nested fields valid for every foreign interface.
- Define panic/unwind behaviour at each boundary according to its ABI. `catch_unwind` catches only unwinding Rust panics, not aborts, and is not a general foreign-exception safety mechanism. Prevent unwinding across boundaries that forbid it; do not claim recovery without restoring invariants.
- Avoid panicking in destructors, especially during unwinding; provide explicit fallible cleanup where callers need the result. Assess blocking cleanup against the actual execution model.
- Add adversarial tests for invalid input, partial initialisation, repeated cleanup, and safe call sequences. Run applicable Miri tests where supported; unsupported FFI or unexercised paths remain gaps. Fuzzing and sanitizers can supplement, not replace, reasoning.

Sources:

- [Rust Reference: undefined behaviour](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)
- [Rustonomicon: FFI](https://doc.rust-lang.org/nomicon/ffi.html)
- [Miri](https://github.com/rust-lang/miri)
