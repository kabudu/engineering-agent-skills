# Debugging

Read when diagnosing or fixing a defect. Use existing repository tools and the shortest investigation that establishes the cause. No particular agent host, language, test framework, or additional skill is required.

## Establish the failure

- Identify intended behaviour, observed behaviour, affected input/state, and the smallest useful reproduction. Inspect the real error and relevant state before changing code.
- Reproduce through the affected interface when practical: a library call, CLI, API, or UI. Record the command or interaction and its failure. A lower-level check may help isolate the cause; state which original boundary it does not exercise.
- If reproduction is unavailable or intermittent, record the attempted conditions, missing access/state, and what the available evidence supports. Use bounded instrumentation or controlled experiments rather than inventing certainty. Do not expand a diagnosis request into product changes or mutate a live system without authorization.

## Establish the cause

- Trace the failure to the first incorrect decision or missing handling, using source, runtime observations, and relevant history. Distinguish documented rationale from inference.
- Test competing explanations with observations that could disprove them. When repeated fixes depend on the same assumption and fail, state and test that assumption before trying another fix.
- Decide whether the triggering state is legitimate. Handle it where the contract requires if it is; otherwise locate its producer. Guards, retries, fallbacks, and swallowed errors need evidence that they address the cause rather than conceal it.
- Remove changes justified only by refuted hypotheses. Preserve unrelated user work; retain useful instrumentation only when it belongs in the requested solution.

## Fix and verify

- Make the smallest change that addresses the demonstrated mechanism while preserving nearby contracts. Check for the same fault in related paths within scope; report broader work rather than silently expanding the task.
- When a practical regression test exists, make it fail for the intended reason before the fix and pass afterwards. Assert behaviour through the relevant contract, including observable side effects. Do not weaken assertions to accommodate incorrect behaviour.
- If a new test needs disproportionate infrastructure, brittle mocks, or unrelated fixture changes, use an existing check or focused reproduction instead. No new harness or separate failing-test commit is required just to satisfy this workflow.
- Rerun the original reproduction and appropriate nearby checks. For intermittent failures, report the conditions and attempts; absence in a short run is limited evidence. If only a substitute check can run, state what remains unverified.

Report the failure, causal evidence, fix if requested, before/after results, and remaining uncertainty. A plausible explanation or a passing substitute is not proof that the original defect is resolved.
