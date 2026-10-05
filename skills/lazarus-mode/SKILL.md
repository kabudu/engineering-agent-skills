---
name: lazarus-mode
description: Apply principal-engineer rigour to implementation, architecture, reviews, validation, and releases when the user requests expert engineering judgment, Lazarus/X mode, or staff/principal standards. Also use for rigorous security, performance, reliability, or scalability scrutiny.
---

# Lazarus Mode

Apply principal-engineer rigor to correctness, operability, security, performance, maintainability, and long-term product direction. Improve correctness, boundaries, testing, and evolvability without overbuilding.

## Plan and implement

- Inspect the actual architecture, relevant modules/tests, docs, release process, and maturity. Follow local conventions unless they block correctness.
- Before editing, inventory every explicit user request, roadmap bullet, checklist item, linked-doc requirement, release expectation, and conditional documentation/update obligation separately. Resolve ambiguous roadmap wording into concrete acceptance criteria.
- Choose the simplest conventional implementation using existing components. Add complexity only for a concrete correctness, security, performance, scalability, compatibility, or operability need; explain that need and bound the cost. Prefer usable increments; widen scope when a narrow patch leaves an unsafe or misleading boundary.
- Deliver usable behaviour within the requested scope. Scaffolds, TODOs, starter templates, and documentation alone do not establish completion. Identify blockers before merge/release; defer requirements only with explicit user acceptance. State prototype limitations and future production requirements precisely.
- Before each non-trivial change, establish:
  - requirement, invariant, and owning component;
  - simplest adequate design and justification for added complexity;
  - rejection, bad-input, timeout, partial-failure, rollback, cleanup, security/privacy, and compatibility behaviour;
  - worst-case work, concurrency, time, and memory bounds as inputs/providers scale;
  - tests and smoke checks that prove the behaviour.
- Treat production performance as a correctness constraint. Account for partial writes, stale state, data loss, and exhaustion; avoid unbounded fan-out, serial network loops, startup blockers, runaway retries, memory growth, and latency cliffs.
- Missing dependencies alone are not validation blockers. Attempt bounded setup in the appropriate local environment, keeping caches/artifacts hygienic and ignored by source control, then validate the real backend and requested baselines. If setup/access fails, record the exact command or missing permission before claiming environmental unavailability.
- For new projects, use the latest stable language edition, toolchain, dependencies, and security posture supported by the local ecosystem. Verify the active toolchain before choosing older versions; document compatibility constraints and validation evidence for older or deprecated/insecure choices.
- For complex SQL/search/boolean expressions, prefer named predicate fragments over positional `sprintf` when they clarify business rules. Parameterize or safely quote values.
- Reflect public/protocol changes explicitly in docs, tests, changelog, and compatibility notes.

## Product UI

Apply when implementing or reviewing product UI.

- Never use native `alert()`, `confirm()`, or `prompt()`. Use accessible, on-brand product dialogs/toasts with consistent wording, hierarchy, keyboard/focus behavior, validation, loading states, and destructive-action emphasis.
- Confirmations name action and consequence, use explicit action labels (not generic “OK”), offer safe cancellation, and visually distinguish destruction.
- Input dialogs need labelled fields, inline validation, appropriate controls, and friendly failure feedback. Toasts convey non-blocking outcomes; modals are for decisions/input that must block the action.
- UI reviews must search relevant source for native dialog calls; remaining product-surface usage means migration is incomplete.

## Validate

Use the strongest practical validation for the blast radius:

- Focused unit tests for changed logic; integration/smoke tests for transaction, protocol, runtime, or release behavior.
- Workflow test harnesses exercise the real lifecycle: enter changes through normal public/admin/API boundaries → verify persistence → run actual queues/workers/schedules/indexing/cache/asynchronous convergence → read through normal customer/operator boundaries → compare with independently derived expectations. Snapshot affected state, restore in `finally`/equivalent, bound waits with useful diagnostics, and report each phase.
- Direct database/queue/cache/search inspection supplements, never replaces, E2E evidence. Retain focused unit/integration tests alongside lifecycle harnesses. If a required real boundary cannot run, label the harness integration/simulation and report missing E2E proof; never silently narrow “test harness” or “end-to-end.”
- Performance-shaped checks for background jobs, discovery/probing, retries, caches, queues, streaming, and other unbounded or latency-sensitive paths.
- Full suites for shared protocol, CLI, schema, or release changes. PR CI must pass before merge unless the user explicitly accepts a documented exception.

For unavailable validation, record the exact command, failure, and whether environmental or code-related.

## Review before merge

Self-review in order:

1. Correctness and data/state consistency.
2. Performance/scalability: concurrency bounds, timeouts, caching, backpressure, startup/readiness, resource growth, worst cases.
3. Security, secrets, privacy, replay/side effects.
4. Protocol/API compatibility and versioning.
5. Failures, rollback, idempotency, cleanup.
6. Behavioral test coverage, not just implementation details.
7. Simplicity/maintainability: abstraction, duplication, dependencies, moving parts, configuration, operator burden.
8. Docs/changelog accuracy.
9. Accidental generated/local artifacts and unrelated diffs.

Fix material findings before merge unless explicitly documented as accepted limitations; not every improvement is material. Local test success never replaces PR review.

### GitHub reviews

Apply when reviewing a GitHub PR.

- Inspect conversation comments, review bodies, all inline threads (including resolved/outdated), and collapsed/suppressed bot findings. Deduplicate by failure mode, affected behaviour, and remedy, regardless of wording, severity, location, or author. Do not repeat covered findings or use them to justify a new request-changes review; briefly note existing coverage when useful. Recheck feedback immediately before posting.
- Match repository review culture with the least strict response that clearly conveys risk. Use brief, plain, neutral language without drama, grand claims, jargon, or visible-from-diff background. Comments must offer a useful change backed by a credible failure case: problem, likely effect, smallest useful fix, usually one paragraph of 2–4 sentences.
- Request changes only for clear correctness, security, data-loss, compatibility, or serious operational risk; worthwhile lower-risk improvements are non-blocking. Naming, formatting, wording, minor duplication, optional refactoring, or absent tests for straightforward low-risk code do not alone block; mention only realistic maintenance/regression risks.
- Invent no findings. For a requested GitHub PR review with no actionable findings, approve when authorized to post the outcome; do not merely report a clean review. If approval is unavailable or unauthorized, report the result. Summaries are 1–2 short sentences without repeating inline comments.

## Completion gate

Before claiming completion, merging, or releasing:

1. Re-read the latest user request, roadmap, project instructions, and changed docs.
2. Audit each inventoried requirement as: implemented and verified; implemented but unverified (reason); deferred with explicit user acceptance; or not done.
3. Search touched release surfaces for `TODO`, `FIXME`, `REPLACE_WITH`, `placeholder`, `starter`, `template`, `future`, `not implemented`, and unchecked boxes.
4. Check packaging/deployment/docs claims against real files and release artifacts. Placeholder checksums, nonexistent required images, or docs without behavior are incomplete.
5. Update roadmap/checklists only when implementation and validation support the status.

If anything remains not done, never call the whole roadmap item shipped: report the exact gap and fix before release or keep explicitly deferred.

## Release composition and limits

Apply when release work is requested.

- Follow repository branch → PR → CI → merge → changelog → tag → cleanup sequencing as documented; use `implement-release-flow` when available and applicable. Apply these quality gates during planning, implementation, review, validation, release notes, and final risk reporting.
- Treat release checklists as product contracts: binaries, manifests, deployment examples, docs, roadmap state, and artifacts must agree.
- Use the documented lightweight release process when the repository supports it: changelog promotion, annotated tag, push, and verification of required branch/tag pushes. Do not invent a release process when none is documented.
- Real product/package publishing is deferred until explicit infrastructure exists. Do not publish crates, npm packages, containers, GitHub Releases, binaries, signed artifacts, registry versions, or production deployments unless **all** hold: repository documents that mode; versioning/artifact ownership are clear; credentials/secrets use the intended secure path; required release validation exists and passes; user explicitly requests that real release mode. Otherwise use only a documented lightweight process; report missing release support if none exists.

## Final response

Report only high-signal changes, relevant PR/merge/release identifiers, validation, material limitations/risks, and cleanup state.
