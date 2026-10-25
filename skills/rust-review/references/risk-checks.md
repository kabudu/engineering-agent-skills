# Additional Rust review checks

Use only the sections relevant to the reviewed change. This reference deliberately stands alone so the review skill can be installed independently.

## Unsafe and foreign boundaries

Trace pointer validity, provenance, alignment, initialisation, bounds, aliasing, lifetime, allocation/free pairing, and thread access. Check the entire safe wrapper lifecycle, including partial failures and repeated calls. Explain a permitted call sequence that violates an invariant before alleging unsoundness. Missing `SAFETY` comments merit a request for justification, not a fabricated UB claim.

Check ABI, representation, callbacks, null pointers, and unwind contracts. `catch_unwind` cannot recover from aborting panics and does not make arbitrary foreign exceptions safe. Inspect destructor behaviour during unwinding. Miri evidence covers exercised supported paths; it is not a universal proof.

## Concurrency and cancellation

Identify the runtime, local versus cross-thread execution, task ownership, lock ordering, suspension points, and shutdown behaviour. A synchronous guard across `.await` needs particular scrutiny; an async guard can be intentional. Check callbacks under locks, contention, bounded work, partial operations on cancellation, retry duplication, and detached failures.

Poison recovery is valid only when protected invariants are established or repaired. Poisoning is advisory; unsafe code cannot rely on it for soundness. Required `Send`/`Sync` contracts depend on the API and execution model, including returned futures.

## Trait laws and public evolution

Check that `Eq`, `Ord`, `PartialOrd`, and `Hash` describe the same semantic value. Derived equality beside custom ordering is valid when they agree; test counterexamples rather than flagging implementation style.

Determine the actual compatibility promise before recommending signature changes, private fields, sealed traits, or `non_exhaustive`. Review downstream implementations/callers and supported feature combinations. Intentional smart pointers or erased errors in public APIs require contract analysis, not blanket rejection.

An `expect` may enforce a proven internal invariant; show how it becomes reachable with invalid state before calling it a bug. Integer casts can truncate without panicking. Check arithmetic modes and input ranges separately.

## Primary references

- [Rust Reference: undefined behaviour](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)
- [Rust Reference: numeric casts](https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast)
- [Ord contract](https://doc.rust-lang.org/std/cmp/trait.Ord.html)
- [Hash contract](https://doc.rust-lang.org/std/hash/trait.Hash.html)
- [Mutex poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html#poisoning)
- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
- [Rustonomicon: FFI](https://doc.rust-lang.org/nomicon/ffi.html)
