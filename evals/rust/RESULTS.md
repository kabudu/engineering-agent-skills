# Rust skill evaluation results

25 October 2026. The primary result is an **18-run preliminary comparison**: six tasks, three conditions, one run per task/condition, using `gpt-6-luna` with low reasoning effort. It measures the Rust skills from commit `34878c5` against BeautifulRust revision `2b2d53a66f6f36ab4b8d6a93070183d91e77fad4` and a control without Rust skills. The skill files were not changed during evaluation.

## Outcome

In the controlled sample, condensed used **27.9% fewer total tokens** and **33.0% less uncached input** than upstream. All three implementation cases passed held-out checks in every condition. The planted-defect review found all three defects in every condition; upstream additionally made an unsupported poison-recovery claim.

**Equivalent reliability and verification depth are not established.** There is only one controlled sample per case, the authoring assistant graded reviews, and the condensed clean-code review skipped available formatting/lint/test checks. An invalidated exploratory repeat also missed two defects under the condensed skill. Follow-up work should refine verification/coverage and repeat the controlled evaluation before claiming equivalent reliability.

The no-skill control also passed the implementation tests and identified all three planted defects in this controlled run, using fewer tokens than either skill condition. These examples therefore do not establish a quality benefit from installing either skill.

## Measured usage

These are actual cumulative Codex CLI `turn.completed.usage` counts, including model input across tool calls, tool results, loaded references, and output. Cached input is a subset of input; reasoning output is retained in raw evidence but not added a second time. These are not word-count estimates or monetary cost calculations.

| Across six tasks | No Rust skill | BeautifulRust | Condensed |
| --- | ---: | ---: | ---: |
| Input tokens | 305,149 | 556,082 | 399,594 |
| Cached input tokens | 277,632 | 460,800 | 335,744 |
| Uncached input tokens | 27,517 | 95,282 | 63,850 |
| Output tokens | 5,923 | 6,876 | 6,397 |
| Total input + output | 311,072 | 562,958 | 405,991 |
| Command calls | 18 | 28 | 24 |
| Model-run elapsed seconds | 88.81 | 103.34 | 90.62 |

Condensed output tokens were 7.0% lower than upstream. Its elapsed time was 12.3% lower in this sample, but machine load, warm caches, and model sampling are uncontrolled; this is not a general speed benchmark. Condensed total tokens were 30.5% higher than the no-skill control.

| Task | No Rust skill: total tokens | BeautifulRust: total tokens | Condensed: total tokens | Condensed reduction vs upstream |
| --- | ---: | ---: | ---: | ---: |
| Borrowing explanation | 10,437 | 10,861 | 10,688 | 1.6% |
| Planted-defect review | 32,895 | 98,294 | 66,131 | 32.7% |
| Clean-code review | 44,046 | 53,142 | 35,465 | 33.3% |
| Refactor | 68,457 | 120,643 | 101,456 | 15.9% |
| Parsing library | 58,096 | 139,420 | 81,183 | 41.8% |
| Aggregation CLI | 97,141 | 140,598 | 111,068 | 21.0% |

The clean-review reduction partly accompanies less validation: condensed only inspected source and manifest, while upstream ran formatting, Clippy, and tests. Do not interpret the full aggregate reduction as equal-work efficiency. The three implementation cases alone used 293,707 condensed tokens versus 400,661 upstream tokens: **26.7% fewer**, with all held-out checks passing; verification sequences still differed.

## Behavioural evidence

| Check | No Rust skill | BeautifulRust | Condensed |
| --- | --- | --- | --- |
| Library held-out boundary tests | Pass | Pass | Pass |
| CLI held-out output, malformed-input, and overflow samples | Pass | Pass | Pass |
| Refactor held-out boundaries and preserved unrelated function bodies | Pass | Pass | Pass |
| Planted defects identified | 3/3 | 3/3 | 3/3 |
| Unsupported correctness claims in planted review | 0 | 1 | 0 |
| Clean review invented a defect | No | No | No |
| Correct two-sentence borrowing explanation | Yes | Yes | Yes |
| Unnecessary skill read for explanation | No | No | No |

All manifests remain identical and dependency-free. Scope checks on unchanged function bodies ignore formatting whitespace. The baseline review's line references for `first` and `wire_len` were inaccurate, though the named functions and diagnoses were identifiable. Optional style advice is not counted as an invented correctness defect.

The upstream review claimed that poison must be cleared after releasing the repaired mutex guard. The [standard-library documentation](https://doc.rust-lang.org/std/sync/struct.Mutex.html#method.clear_poison) explicitly demonstrates clearing poison while retaining the recovered guard. The fixture restores the vector to an empty valid state under the lock. This is a false positive for the supplied code.

Review grading is a manual assessment by the authoring assistant, not an independent blinded judge. Implementation outcomes come from executable held-out tests added after each model run. The unsafe fixture was never executed; compilation and static inspection do not prove soundness.

## Controls and reproducibility

- Codex CLI `0.164.0-alpha.11.1`, rustc `1.97.0`, one worker, 600-second per-run timeout. No primary run failed or timed out.
- Fresh crates with identical manifests and task fixtures. They begin as untracked files in a new local Git repository; this is synthetic task context, not an established production checkout.
- Same configured model, reasoning setting, permissions, tools, and task specification across conditions. The model alias is not an immutable serving snapshot; model sampling is not seeded.
- User configuration/rules, project instructions, memories, plugins, apps, web search, and multi-agent tools disabled. Personal skills disabled by SKILL.md path, including canonical symlink targets.
- **A no-model app-server `skills/list` preflight verified no enabled skills in control and exactly `rust-best-practices`/`rust-review` in both treatments.** The verified catalogues are saved in metadata.
- Both Rust skills installed for each treatment. Explicit invocation for implementation/reviews; implicit discovery for the explanation. No standalone-review installation or cross-host compatibility experiment was performed.
- A recorded seed shuffles condition order within balanced task blocks. Cache state is not reset; cached and uncached counts are reported separately.
- The three implementation prompts specify fixed interfaces so independent tests do not depend on subjective adapters. Full prompts, generated sources, commands, checks, hashes, and responses are published below.

Primary evidence: [runs.json](results/2026-10-25-luna-isolated/runs.json), [summary.json](results/2026-10-25-luna-isolated/summary.json), [grades.json](results/2026-10-25-luna-isolated/grades.json), [metadata.json](results/2026-10-25-luna-isolated/metadata.json). Recompute the usage summary with:

```sh
python3 evals/rust/summarise_comparison.py evals/rust/results/2026-10-25-luna-isolated
```

The runner uses [Codex non-interactive JSON output](https://learn.chatgpt.com/docs/non-interactive-mode) and verifies discovery through [app-server skills/list](https://learn.chatgpt.com/docs/app-server#skills). Raw authentication, account state, and session logs are excluded from published artifacts.

## Invalidated pilots and stopping point

Earlier GPT-6.1 Sol attempts were heavily rate-limited; ten completed exploratory runs are excluded from the main comparison. A GPT-6 Luna pilot completed 29 runs before additional repetitions were stopped following the user's choice of an 18-run preliminary report.

That pilot's personal-skill disable list used directory paths instead of SKILL.md paths and missed symlinked folders. The intended catalogue isolation was therefore not established. Its first balanced pass used **5.1% more** condensed total tokens, and a subsequent condensed review found only the unsafe slice defect, missing the panic and truncating cast. The pilot is retained [with all completed records](results/2026-10-25-luna-pilot/README.md), clearly invalidated and excluded from primary estimates. The replacement 18 runs use corrected, verified isolation; changes in results cannot be attributed solely to that correction rather than sampling variation.

Do not pool models, pilot runs, or unbalanced repetitions. The 54-run repeated benchmark was not completed. The published totals describe the primary 18 reported turns, not all allowance consumed during setup, pilot work, or retries.

## Entrypoint compression and local checks

Counts use Python whitespace splitting of complete SKILL.md files, including metadata and attribution. References are excluded; these are not tokenizer measurements.

| Entrypoint | Upstream words | Adapted words | Reduction |
| --- | ---: | ---: | ---: |
| rust-best-practices | 4,422 | 912 | 79.4% |
| rust-review | 1,224 | 542 | 55.7% |
| Combined | 5,646 | 1,454 | 74.2% |

Both skill-format validators pass. The local fixture checker compiles the unsafe fixture without running it, passes the clean fixture's boundary test, and checks local links and retained MIT notices. Licence files match upstream byte-for-byte. The refactor grader was checked against both an allowed signature/documentation change and an unrelated behavioural mutation. Whitespace checks pass.

## Recommended next iteration

Make review completion explicit: check the remaining scoped input boundaries and error paths after finding a severe bug. Make the required available validation checks and acceptable reasons for skipping them clearer. Batch independent context reads and avoid redundant checks where this preserves verification. Then repeat the controlled comparison with a fixed minimum verification contract and more realistic API, feature/MSRV, async/cancellation, and FFI cases. Keep measured revisions separate; do not retrofit favourable claims onto an untested edit.
