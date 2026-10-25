# Concurrency and async decisions

Read when changing shared state, futures, blocking work, or cancellation behaviour.

- Establish the execution model: single-threaded or multithreaded runtime, task ownership, shutdown, cancellation, and required `Send`/`Sync` guarantees. Do not impose `Send` on deliberately local futures or assume all libraries are runtime-independent.
- Keep related invariants under a coherent synchronisation boundary. Bound critical sections and avoid user callbacks while holding locks unless the contract explicitly handles reentrancy. Check lock ordering, deadlocks, starvation, and resource growth.
- Inspect guards and borrows across `.await`. A synchronous mutex held while suspended can block progress or deadlock; an async guard across `.await` may be intentional but still needs contention and cancellation analysis. Do not replace locks solely to silence a compiler diagnostic.
- Mutex poisoning signals potentially broken invariants. Propagate failure or recover only after establishing or restoring those invariants; never blindly ignore poison. Poisoning is advisory and cannot be the basis of unsafe-code soundness.
- Keep blocking I/O and substantial CPU work off executor threads using the runtime's supported facilities. Bound concurrency and queue growth. Cooperative yielding is not a universal substitute for moving sustained blocking work; choose budgets from measured workload needs.
- Check cancellation between operations: partial state updates, lost messages, abandoned resources, retries, idempotency, and shutdown joins. Detached tasks need explicit ownership and failure handling.
- Assert required `Send`/`Sync` contracts with compile checks when regression risk warrants them. Test the relevant futures, not only the type that constructs them.
- Exercise contention, cancellation, failure, and shutdown paths with bounded tests. Timing-only sleeps are weak evidence; prefer controlled synchronisation and explicit completion conditions.

Sources:

- [Mutex poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html#poisoning)
- [Send](https://doc.rust-lang.org/std/marker/trait.Send.html) and [Sync](https://doc.rust-lang.org/std/marker/trait.Sync.html)
- Consult the project's runtime documentation for blocking, cancellation, and scheduling contracts.
