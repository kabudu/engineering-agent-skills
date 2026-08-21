---
name: lazarus-mode
description: Use when the user asks for expert-level engineering judgment, "X mode", seasoned/staff/principal engineer standards, robust architecture, security/performance/reliability/scalability scrutiny, optimization review, rigorous implementation and release discipline, or when combining implementation work with implement-release-flow. Applies as a rigor overlay for code design, testing, reviews, documentation, and lightweight roadmap releases. Do not use to perform real package/product publishing unless the repository explicitly supports that release mode.
---

# Lazarus Mode

## Purpose

Lazarus Mode is an expert-engineering rigor overlay. Use it to make implementation decisions as if the work will be reviewed by a principal engineer responsible for correctness, operability, security, performance, maintainability, and long-term product direction.

This is not a license to overbuild. The output should be more correct, better bounded, better tested, and easier to evolve.

## Operating Rules

- Start from the repository's actual architecture, docs, tests, release process, and current maturity.
- Default to the simplest architecture and implementation that fully satisfies the proven requirements. Prefer clear, conventional, maintainable code and existing components over new abstractions, services, dependencies, indirection, or operational machinery. Introduce complexity only when a concrete correctness, security, performance, scalability, compatibility, or operability requirement makes the simpler approach insufficient; state that requirement and keep the added complexity narrowly bounded.
- Treat ambiguous roadmap wording as a design problem: define the concrete acceptance criteria before editing.
- Build a requirement inventory before implementation. Extract every explicit user request, roadmap bullet, checklist item, linked doc requirement, release-process expectation, and "where relevant" documentation/update obligation into a working checklist. Do not collapse separate deliverables into a broad label.
- Do not mark an item complete because a scaffold, placeholder, TODO, starter template, or documentation-only note exists. Count it complete only when it is usable by the intended operator/developer in the repository's release context, or explicitly mark it as a documented limitation accepted by the user.
- Prefer doing the difficult-but-bounded work over narrowing the requirement to the easy subset. If a requirement is feasible within the current repo and requested release scope, implement it; if it is not feasible, state the blocker before merge/release and leave the item unchecked or documented as deferred.
- Missing local packages, SDKs, runtimes, toolchains, or framework backends are not blockers by themselves. When they are reasonably installable and relevant to the requested proof, first attempt a bounded installation in the project-appropriate local environment, with disk/cache hygiene and source-control ignores, then validate with the real backend. This explicitly includes ML packages and accelerator stacks such as PyTorch, MLX, NumPy/SciPy, Metal/Xcode command line tools, and benchmark/test dependencies. Do not skip a requested baseline, validation path, or backend merely because the package is absent at first inspection. Treat unavailability as a blocker only after installation or access attempts fail for concrete environmental reasons, and record the exact failed command or missing system permission.
- For new projects, default to the latest stable language edition, toolchain, dependency versions, and security posture that the local/current stable ecosystem supports. Verify the active toolchain before downgrading editions or pinning older dependency families. If compatibility requires an older edition, runtime, package version, or insecure/deprecated dependency, document the concrete constraint and validation evidence instead of silently choosing the older default.
- Prefer narrow, production-shaped increments over broad speculative abstractions.
- When constructing complex SQL, search, or boolean conditions, prefer named predicate fragments composed into the final expression over positional `sprintf` templates when this makes the business rules easier to read and review. Keep values parameterized or safely quoted, and use formatters only when they are genuinely clearer.
- Identify failure modes before choosing the implementation: rollback, partial writes, stale state, concurrency, unbounded work, timeouts, resource exhaustion, compatibility, security, data loss, privacy, and user-visible behavior.
- Treat performance and scalability as correctness constraints for production paths: avoid unbounded fan-out, serial network loops, startup blockers, runaway retries, excessive memory growth, and hidden latency cliffs.
- Make public or protocol-facing changes explicit in docs, tests, changelog, and compatibility notes.
- Use existing local conventions unless they are actively blocking correctness.
- Do not hide prototype limitations. Document them precisely and name the future production requirement.

## Implementation Standard

Before editing, inspect the relevant modules and tests. For each non-trivial change, decide:

- **Simplicity:** What is the least complex approach that satisfies the requirements, and what concrete evidence justifies any added abstraction or operational burden?
- **Invariant:** What must always remain true?
- **Boundary:** Which component owns the behavior?
- **Failure path:** What happens on rejection, timeout, partial failure, or bad input?
- **Performance path:** What is the expected work per request/job, what bounds concurrency/time/memory, and what happens as inputs or providers scale?
- **Compatibility:** What existing users, fixtures, or scripts must keep working?
- **Evidence:** What tests or smoke checks prove the behavior?

Implementation should be scoped, but not superficial. If the smallest change would create a misleading or unsafe behavior, widen the scope enough to fix the actual boundary.

## UI Conventions

- Never use browser-native `alert()`, `confirm()`, or `prompt()` in a product interface. Use the product's accessible, on-brand modal/dialog and toast components so wording, visual hierarchy, keyboard behavior, focus management, validation, loading states, and destructive-action emphasis remain consistent.
- Confirmation dialogs must name the action and consequence, use explicit action labels instead of generic "OK", provide a safe cancel path, and visually distinguish destructive actions.
- Input dialogs must use labelled fields, inline validation, appropriate input controls, and user-friendly failure feedback. Use toasts for non-blocking outcomes and reserve modals for decisions or input that must block the current action.
- During UI reviews, search the relevant source tree for native dialog calls and treat any remaining product-surface usage as an incomplete migration.

## Completion Gate

Before claiming completion, merging, or releasing, perform a requirement-by-requirement audit:

1. Re-read the user's latest request, roadmap text, project instructions, and changed docs.
2. For every requirement, record one of: implemented and verified; implemented but unverified with reason; deferred with explicit user acceptance; or not done.
3. Search for placeholder markers and incomplete language in touched release surfaces: `TODO`, `FIXME`, `REPLACE_WITH`, `placeholder`, `starter`, `template`, `future`, `not implemented`, and unchecked checklist boxes.
4. Verify packaging, deployment, and documentation claims against actual files and release artifacts. A package manifest with placeholder checksums, a manifest requiring a nonexistent image, or docs without backing behavior is not complete.
5. Update roadmap/checklist state only after the implementation and validation evidence support it.

If any item is not done, do not describe the whole roadmap item as shipped. Report the exact gap and either fix it before release or keep it explicitly deferred.

## Review Standard

Run a self-review before merge using this order:

1. Correctness and data/state consistency.
2. Performance and scalability: bounded concurrency, timeouts, caching, backpressure, startup/readiness impact, resource growth, and worst-case behavior.
3. Security, secrets, privacy, and replay/side-effect risk.
4. Protocol/API compatibility and versioning impact.
5. Failure behavior, rollback, idempotency, and cleanup.
6. Test coverage against behavior, not only implementation details.
7. Simplicity and maintainability: unnecessary abstraction, duplication, dependencies, moving parts, configuration, and operator burden.
8. Documentation and changelog accuracy.
9. Accidental generated files, local artifacts, or unrelated diffs.

Material findings should be fixed before merge unless explicitly documented as accepted limitations. Do not treat every improvement as material.

### GitHub Code Review Style

Keep GitHub reviews practical, brief, and proportionate to the change.

- Before reporting or posting findings, inspect all existing PR feedback: conversation comments, submitted review bodies, inline threads (including resolved and outdated threads), and collapsed or suppressed findings included in bot review summaries.
- Build a semantic inventory of existing findings by failure mode, affected behavior, and requested remedy. Treat a candidate as already covered when those materially match, even if its wording, severity, location, author, or presentation differs.
- Do not repeat an already-covered finding in the review output, create another inline comment for it, or use it as the basis for a new request-changes review. If useful, state only that existing feedback already covers the issue and focus the review on unique findings.
- Re-check existing feedback immediately before posting a review so comments added during the review are also deduplicated.
- Use plain, neutral language. Avoid dramatic wording, colourful phrases, grand claims, and unnecessary engineering jargon.
- State the problem, its likely effect, and the smallest useful fix. Usually keep each comment to one short paragraph of two to four sentences.
- Do not write an essay for a simple code pattern. Omit background the author can already see from the diff.
- Leave a comment only when it gives the author something useful to change. Do not restate the diff or add speculative concerns without a credible failure case.
- Request changes only for a clear correctness, security, data-loss, compatibility, or serious operational risk. Use a non-blocking comment for worthwhile but lower-risk improvements.
- Do not block a PR only for naming, formatting, wording, minor duplication, optional refactoring, or missing tests for straightforward low-risk code. Mention these only when they create a realistic maintenance or regression risk.
- Match the repository's normal review culture. Prefer the least strict response that still communicates the risk clearly.
- If the user asks for a GitHub PR review and there are no actionable findings, approve the PR when their request authorizes posting the review outcome. Do not merely report that no feedback needs to be addressed. For reviews where approval is unavailable or not authorized, report the result without inventing a finding.
- Keep the overall review summary to one or two short sentences. Do not repeat every inline comment.

## Validation Standard

Run the strongest practical validation for the blast radius:

- Focused unit tests for changed logic.
- Integration/smoke tests for transaction, protocol, runtime, or release behavior.
- When creating a test harness for a user-facing or operational workflow, make the
  harness exercise the real end-to-end lifecycle exactly as the system is used:
  enter changes through the normal public/admin/API boundary; verify persistence;
  run the actual queue, worker, scheduled job, indexing, cache, or asynchronous
  convergence path; read the outcome through the normal customer/operator-facing
  boundary; and compare observed behavior with independently derived expectations.
  Snapshot affected state first, restore it in a `finally`/equivalent cleanup path,
  bound all waits with useful diagnostics, and report each lifecycle phase.
- Treat direct database, queue, cache, or search-engine inspection as additional
  evidence and troubleshooting support, not a substitute for the end-to-end path.
  Keep focused unit and integration tests in addition to the lifecycle harness.
  If an environment cannot exercise a required real boundary, label the harness
  accurately as an integration/simulation harness and report the missing E2E proof;
  do not silently narrow the meaning of "test harness" or "end-to-end."
- Performance-shaped tests or checks for changed background jobs, discovery/probing loops, retry paths, caches, queues, streaming paths, and other potentially unbounded or latency-sensitive work.
- Full test suites when the change touches shared protocol, CLI, schema, or release surfaces.
- CI must pass before merge when a PR workflow exists.

If validation cannot run, document the exact command, failure, and whether the blocker is environmental or code-related.

## Composition With Release Workflows

When Lazarus Mode is used alongside a repository's release workflow:

- Follow the repository's documented branch, PR, CI, merge, changelog, tag, and cleanup sequencing. When `implement-release-flow` applies, use it to drive that sequencing.
- Use Lazarus Mode as the quality gate inside each phase: planning, implementation, review, validation, release notes, and final risk statement.
- Treat the release checklist as a product contract: binaries, package manifests, deployment examples, docs, roadmap status, and release artifacts must agree with each other.
- Do not skip PR review just because local tests pass.
- Do not merge until CI is green unless the user explicitly accepts a documented exception.
- During release, perform the repository's current lightweight release only: changelog promotion, annotated git tag, push, and verification.

## Real Release Exception

Real product/package releases are intentionally deferred until the project has explicit release infrastructure.

Do not publish crates, npm packages, containers, GitHub Releases, binaries, signed artifacts, package registry versions, or production deployments unless all are true:

- The repository documents that release mode.
- Versioning and artifact ownership are clear.
- Credentials/secrets are configured through the intended secure path.
- Required release validation exists and passes.
- The user explicitly asks for that real release mode.

Until then, a "release" means the repository's documented lightweight release process, such as changelog updates, annotated git tags, pushed branches or tags, and verification.

## Final Answer Standard

Report only the highest-signal facts:

- What changed.
- PR/merge/release identifiers when relevant.
- Validation performed.
- Material limitations or risks.
- Cleanup state.
