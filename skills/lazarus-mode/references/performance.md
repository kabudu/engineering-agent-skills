# Performance measurement

Read when investigating measured slowness, comparing performance, or reporting a measured speedup/regression. Use available repository harnesses and platform-appropriate tools; no fixed profiler, runtime, model, or sample count is required.

## Define the comparison

- State the claim, metric and unit, workload, and conditions before interpreting results. Distinguish a rough observation, microbenchmark, end-to-end comparison, and adoption recommendation.
- Record revisions, runtime/dependency versions, build mode, relevant configuration, data size, concurrency, and cache/warmup conditions. Keep sides comparable; name intentional differences. A comparison of shipped defaults is valid when described as such, not as a universal implementation ranking.
- Read the measurement code. Identify the timed region, completed work, error handling, and what the measurement excludes. Reuse a suitable harness before building another.

## Check that the measurement is real

- Confirm the intended work completes inside the timed region. Await asynchronous work, consume lazy results, and check outputs and effects. Fast errors, skipped work, cached results, and no-ops must not masquerade as improvements.
- Count failures, timeouts, retries, and completed operations alongside timing. Compare the same successful work; report changed failure rates rather than hiding them in an aggregate.
- Check machine contention and load-generator capacity. Use comparable warm/cold states and alternate or interleave baseline/candidate runs where drift could bias the result. Keep diagnostic profiling separate from timing runs when it changes the workload.
- Repeat enough to distinguish the claimed change from noise. Report run count and spread alongside a representative statistic. A requested ballpark may use one run if labelled; it does not establish a reliable winner. Treat a small or unstable gap as inconclusive rather than imposing an arbitrary sample quota or statistical test.

## Explain and act on the result

- Investigate the limiting resource or code path with profiling or counters when diagnosing the cause or making a consequential optimization decision. Separate measured mechanisms from hypotheses. Missing causal evidence limits the explanation even when timing differences are repeatable.
- Sanity-check against resource limits and the share of total time affected. Relate a microbenchmark gain to a representative user-visible path before claiming an application-level improvement. Do not extrapolate beyond measured workloads.
- For iterative optimization, change one hypothesis at a time, hold the measurement method stable, and rerun correctness checks. Retain justified improvements; remove unsuccessful speculative changes. If the harness changes, establish a new comparable baseline rather than mixing results.
- Stop when the requested target is met, further experiments are disproportionate, or a concrete blocker prevents reliable measurement. Do not add unattended loops, minimum iteration targets, or infrastructure merely to produce a favourable number.

Report the supported verdict, before/after values and units, workload, run count, variation, correctness/error results, and relevant environment. Link detailed evidence where useful. Distinguish no measurable difference from insufficient evidence, and state limits on causal or end-to-end claims.
