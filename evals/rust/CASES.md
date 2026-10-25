# Rust skill behavioural evaluations

Keep this file away from the agent performing each task: it contains grading criteria. Use isolated temporary workspaces. Never execute the unsafe `view` fixture; compile it only. These cases require no registry downloads.

| Case | Task given to the agent | Observable success criteria |
| --- | --- | --- |
| library | Implement a dependency-free Rust library parsing exactly three decimal u16 components separated by dots. Reject whitespace, signs, leading zeroes except zero itself, missing/extra components, and overflow. Expose read-only accessors, FromStr, and a public error implementing Error. Add tests. | Compiles; accepts 0.1.65535; rejects empty input, 01.2.3, +1.2.3, 1.2, 1.2.3.4, and 65536.0.0; no parse panic; error is usable by a caller; no unrequested semver extensions. |
| cli | Implement a dependency-free CLI counting valid lines from stdin containing exactly a category and a u64 separated by one comma. Skip malformed lines and report their count on stderr. Print category totals sorted by category. Return an error on accumulation overflow. | Deterministic ordering; malformed input does not panic; stdout/stderr are separated; overflow is detected; duplicate categories accumulate correctly; tests exercise input and overflow boundaries. |
| refactor | Refactor first and wire_len from fixtures/review.rs to eliminate failures from externally supplied input. Public signature changes are allowed but must be explained. Do not change other functions. | Empty input is represented explicitly; length 256 cannot silently become 0; tests establish boundary behaviour; view and intentional APIs are untouched; signature migrations are reported. |
| review | Review fixtures/review.rs for correctness and soundness. Do not modify the file. | Identifies first's empty-input panic, wire_len's loss of length above 255 (not a panic), and view's out-of-bounds slice construction despite its SAFETY comment. Does not execute view. Does not allege that Arc, consistent derived equality/custom ordering, the literal expect, or invariant-restoring poison recovery are inherently defective. |
| clean-review | Review fixtures/clean.rs for actionable correctness defects. Do not modify the file. | No invented findings or demand for a minimum count/praise section. Reports actual checks and their limits. |
| scope | Explain what borrowing means in Rust in two sentences. | Answers the question without running a crate workflow, editing files, or loading specialised references. |

For review grading, count distinct real defects found, missed defects, incorrect severity, unsupported claims, and proposed breaking changes. A stylistic suggestion is not itself a false positive if explicitly optional, but should not obscure defects.

For implementation grading, use independent integration tests derived from the requested contract; test actual CLI exit codes and stdout/stderr. Do not grade generated prose, exact type names, or presence of particular source tokens.
