# Rust skill evaluation protocol

Compare three conditions: no Rust skill, BeautifulRust at revision `2b2d53a66f6f36ab4b8d6a93070183d91e77fad4`, and these condensed skills. Use the same agent/model version, reasoning settings, tool permissions, task prompt, and initial workspace. Keep unrelated personal skills out of every condition. A host that ignores skill routing cannot establish discovery quality.

Run each case in CASES.md in a fresh workspace/session. Supply only its task and required fixture; withhold the rubric. Use at least three runs per condition for a preliminary comparison, randomise condition order, and report variability. Use the writing skill for implementation and the review skill for reviews. Evaluate automatic selection separately from explicitly loading a skill, including the scope case and review independence with only rust-review installed.

Record revision, model/settings, task, condition, loaded files, tool calls, input/output tokens (cached tokens separately when available), elapsed time, executed checks, and grading evidence. Token accounting must include selectively read references and tool output. Report total cost as well as entrypoint size; output growth can erase input savings. If a host exposes no token counts, label the measurement unavailable rather than substituting word counts.

Grade observable results against CASES.md and independently derived tests. Compare correctness, missed defects, false positives, scope creep, and validation honesty. Inspect reference routing: specialised tasks should load the relevant reference; ordinary tasks should not read them all. Treat a failed safety case as a release concern regardless of average score.

Do not claim equivalent effectiveness from static validation, fixture compilation, self-review, or a single run. Publish comparative results only after completing the same matrix for all conditions, with failures and uncertainty visible.

## Local fixture checks

Run `python3 evals/rust/check_fixtures.py` from the repository root. It compiles the review fixture without executing its unsound function, runs clean-fixture tests, validates local Markdown links and retained licences, and reports word/byte counts. It uses temporary output directories and no dependencies beyond Python and rustc. These checks validate the evaluation inputs and packaging, not agent performance.

## Status

An 18-run controlled GPT-6 Luna preliminary comparison is complete. See [RESULTS.md](RESULTS.md) for actual token counts, held-out test outcomes, verification gaps, and invalidated-pilot disclosures. Repeated-run equivalence and general savings remain unverified.

## Run the comparison locally

Requires an authenticated Codex CLI supporting `exec --json`, `--ignore-user-config`, and the configuration keys used by the runner, plus Rust/Cargo on PATH. These model runs consume the account's Codex allowance. Use a model available to the account; the example preserves the model used for this evaluation.

```sh
git clone https://github.com/morganlinton/BeautifulRust /tmp/beautifulrust-eval-upstream
git -C /tmp/beautifulrust-eval-upstream checkout 2b2d53a66f6f36ab4b8d6a93070183d91e77fad4
python3 evals/rust/run_comparison.py \
  --upstream /tmp/beautifulrust-eval-upstream \
  --output /tmp/rust-skill-comparison \
  --model gpt-6-luna --workers 1 --repeats 1
python3 evals/rust/summarise_comparison.py /tmp/rust-skill-comparison
```

The default `--repeats 1` runs an 18-run preliminary comparison. Use `--repeats 3` only when a full 54-run comparison is desired. Reusing the output directory resumes successful runs and archives unfinished attempts; mismatched models, skill contents, or verified catalogues require a new directory. The scheduler prioritises balanced task blocks before later repetitions, randomising condition order within each block using a recorded seed. Rate limits can substantially extend runtime; the runner honours CLI retries and bounds each attempt with a timeout. Ctrl-C or SIGTERM stops active model processes and prevents queued calls from starting.

Before spending model tokens, an app-server skills/list preflight verifies the exact enabled catalogue for each condition. The runner disables personal skills (including symlink targets, using SKILL.md paths), bundled skills, user configuration/rules, project instructions, memories, plugins, apps, multi-agent tools, and web search for these synthetic tasks. It uses fresh crates and copies only the tested skills; upstream eval rubrics are removed. Implementation prompts explicitly invoke the relevant skill; the borrowing explanation tests automatic routing. Both skills are installed for the main comparison, matching upstream's recommended installation. Review-only independence and broader automatic discovery require separate experiments.

The independent implementation checks use fixed public interfaces to avoid subjective adapters: Version's three accessors and FromStr, CSV-like CLI stdout/stderr, and Option/Result boundaries for the refactor. These make prompts more specific than the short descriptions in CASES.md; all conditions receive the same task specification. Grader tests are added only after model execution. Review and explanation outcomes require inspecting the saved responses; summarise_comparison.py never silently marks those as quality passes.

To publish an evidence subset without runtime state or credentials:

```sh
python3 evals/rust/export_comparison.py /tmp/rust-skill-comparison /tmp/rust-skill-evidence --repeat 1
```

Inspect the export before committing. It whitelists run metadata, response text, commands, token counts, test evidence, and generated Rust sources. Raw session events and authentication are excluded.
