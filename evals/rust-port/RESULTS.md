# Rust port smoke validation

26 October 2026. Two standalone functional cases ran on GPT-6 Luna with low reasoning effort. The catalogue preflight verified that only `rust-port` was enabled. Neither the Rust writing nor review skill was installed in these temporary workspaces.

| Case | Original tests | Independent Rust contract tests | Original source preserved | Porting notes |
| --- | --- | --- | --- | --- |
| C byte parser | Pass | 3 tests pass | Yes | API/test mapping and actual check results reviewed |
| Python line splitter | 4 tests pass | 2 tests pass | Yes | API/test mapping and actual check results reviewed |

The C checks cover non-UTF-8/NUL keys, nullable input, numeric limits, error precedence, and integration with `std::error::Error`. The Python checks cover all listed Python separators, non-ASCII text, non-separator control characters, empty lines, and whitespace preservation. The model's own ported tests passed as well. Recorded commands confirm that the verification claims in the notes correspond to executed checks.

An initial C port passed behavioural boundaries but omitted the standard public error traits. Review identified the gap; the skill was clarified and an independent trait-contract test was added. That check rejected the initial C artifact. Both cases were rerun using the revised skill and passed. The initial outputs are retained alongside the final evidence rather than being counted as passing the stricter contract.

Evidence: [final results](results/2026-10-26/results.json), [initial outputs](results/2026-10-26/initial-results.json), and [metadata](results/2026-10-26/metadata.json). Records include prompts, generated Rust and porting notes, command outcomes, enabled skills, token usage, and skill-file hashes. Runtime authentication and raw session state are excluded.

Additional local validation:

- Portable checker and 23 mutation tests pass on Python 3.9.6 and 3.14.6, using PyYAML 6.0.3.
- All three Rust skill packages pass format, link, and retained-licence checks; the existing Rust fixtures pass.
- A local Clippy probe on rustc 1.97.0 confirmed that `allow_attributes` and `allow_attributes_without_reason` are suppressed with declared MSRV 1.80, and fire at 1.81 or with no declared MSRV. The note describes the declared-MSRV restriction, not a requirement that every crate set that field.

These are two small tasks, with authoring-assistant review and no control condition. They do not establish general correctness, performance gains, compatibility across all source languages, or equivalent reliability to upstream. The historical Rust comparison and its pins are unchanged. See [the smoke protocol](README.md) to reproduce these cases explicitly; CI runs only static checks and the source oracles.
