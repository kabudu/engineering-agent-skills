# Rust skill evaluation protocol

Compare three conditions: no Rust skill, BeautifulRust at revision `2b2d53a66f6f36ab4b8d6a93070183d91e77fad4`, and these condensed skills. Use the same agent/model version, reasoning settings, tool permissions, task prompt, and initial workspace. Keep unrelated personal skills out of every condition. A host that ignores skill routing cannot establish discovery quality.

Run each case in CASES.md in a fresh workspace/session. Supply only its task and required fixture; withhold the rubric. Use at least three runs per condition for a preliminary comparison, randomise condition order, and report variability. Use the writing skill for implementation and the review skill for reviews. Evaluate automatic selection separately from explicitly loading a skill, including the scope case and review independence with only rust-review installed.

Record revision, model/settings, task, condition, loaded files, tool calls, input/output tokens (cached tokens separately when available), elapsed time, executed checks, and grading evidence. Token accounting must include selectively read references and tool output. Report total cost as well as entrypoint size; output growth can erase input savings. If a host exposes no token counts, label the measurement unavailable rather than substituting word counts.

Grade observable results against CASES.md and independently derived tests. Compare correctness, missed defects, false positives, scope creep, and validation honesty. Inspect reference routing: specialised tasks should load the relevant reference; ordinary tasks should not read them all. Treat a failed safety case as a release concern regardless of average score.

Do not claim equivalent effectiveness from static validation, fixture compilation, self-review, or a single run. Publish comparative results only after completing the same matrix for all conditions, with failures and uncertainty visible.

## Local fixture checks

Run `python3 evals/rust/check_fixtures.py` from the repository root. It compiles the review fixture without executing its unsound function, runs clean-fixture tests, validates local Markdown links and retained licences, and reports word/byte counts. It uses temporary output directories and no dependencies beyond Python and rustc. These checks validate the evaluation inputs and packaging, not agent performance.

## Status

No comparative model runs have been performed. Behavioural equivalence and total-token savings are unverified. See RESULTS.md for measured packaging results and the exact scope of local checks.
