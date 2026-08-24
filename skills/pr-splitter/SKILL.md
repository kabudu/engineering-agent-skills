---
name: pr-splitter
description: Analyse an oversized pull request or proposed branch changeset and decompose it into smaller, dependency-aware, independently reviewable pull requests. Use when a PR is too large for effective review or when the user asks to split, stack, or repackage a feature branch without changing its final behaviour. Do not use for ordinary PR review or simple branch cleanup.
---

# PR Splitter

## Purpose

Turn one oversized PR into a coherent review series whose combined result is equivalent to the original changeset. Choose boundaries from product behaviour, architecture, data dependencies, and validation needs—not file counts or arbitrary line limits.

## Authorization Boundary

Treat analysis and execution as separate modes.

- A request to analyse, assess, plan, or propose a split is read-only. Do not create or push branches, open PRs, post comments, change the original PR, or rewrite commits.
- Create branches or PRs only when the user explicitly asks to perform the split. Confirm the repository, original PR or head branch, base branch, fork/canonical remotes, and whether the original PR should remain open as an umbrella.
- Never merge or close the original or child PRs unless separately authorized.
- Recheck authorization immediately before pushing branches, creating PRs, or editing the original PR description/comments.

## Establish the Changeset

1. Read repository instructions and inspect the clean/dirty state before changing anything.
2. Fetch the relevant remotes and resolve the exact base, PR head, merge base, and current remote commit IDs. Detect a head update before any later mutation.
3. Inspect PR title/body, reviews, linked issues, CI, commit history, diff statistics, changed paths, and repository ownership boundaries when available.
4. Define the canonical changeset as the base-to-head diff. Do not assume the commit sequence already represents good review boundaries.
5. Inventory behaviour, schema/migrations, generated output, configuration, tests, documentation, operational scripts, and release notes. Identify cross-repository or unpublished-package dependencies.

## Design the Split

Read [references/decomposition-playbook.md](references/decomposition-playbook.md) when choosing boundaries or executing a split.

Build a dependency graph before proposing branches. Prefer slices that each have one clear purpose, a bounded blast radius, meaningful validation, and a reviewer who can understand the change without reconstructing later PRs.

Choose one topology:

- **Sibling PRs:** each branch targets the original base and is independently mergeable. Prefer this when slices are genuinely independent.
- **Stacked PRs:** each branch targets the preceding slice. Use this when schema, shared contracts, generated models, or foundational refactors must land first.
- **Hybrid:** independent sibling groups containing short internal stacks. Use only when it makes the dependency graph materially clearer.

Do not force independence by duplicating code, weakening tests, introducing temporary compatibility paths, or splitting generated output from its source definition. Avoid PRs that are only mechanical leftovers unless they are a legitimate prerequisite with their own validation.

## Analysis Deliverable

Before execution, present a decomposition plan containing:

- original PR/head/base and pinned commit IDs;
- recommended topology and why;
- ordered slice names and concise purposes;
- base branch and dependency for every slice;
- principal paths/behaviours included;
- migrations, generated artifacts, configuration, tests, docs, and changelog ownership;
- validation required per slice;
- cross-slice risks and reviewer notes;
- coverage proof that every original change is assigned exactly once or intentionally superseded.

Flag slices that cannot safely be reviewed or merged independently. Prefer fewer coherent PRs over many tiny PRs.

## Execute an Approved Split

1. Record all starting refs and verify the remote PR head has not moved.
2. Preserve tracked and untracked user work. Use isolated worktrees when practical.
3. Create predictably named branches from the exact approved base or parent slice. A useful pattern is `split/<ticket-or-pr>/<nn>-<purpose>`.
4. Reuse whole commits only when they already match a slice. For tangled commits, repartition the diff semantically; do not preserve poor commit boundaries at the cost of poor PR boundaries.
5. Keep migrations with the first code that requires them, generated artifacts with their source/schema change, and tests with the behaviour they prove.
6. Validate each slice against its declared base before pushing. A stacked child must be tested with its parent applied, not against the ultimate base alone.
7. Compare the final reconstructed stack/group against the original head. The aggregate tree and intended behaviour must match, except for explicitly documented cleanup approved by the user.
8. Push only approved split branches. Use leases for any rewritten remote branch and never overwrite the original PR head unless explicitly requested.
9. Create child PRs with concise descriptions that state purpose, dependency/base, scope, validation, and `Part N of M` linkage to the original PR.
10. Link every child from the original umbrella PR and every child back to the umbrella. For stacked PRs, also link the immediate predecessor/successor and state the required merge order.

## Completion Gate

Do not call the split complete until:

- every original changed path and semantic change is accounted for;
- each child diff is reviewable against its actual base;
- required tests and repository checks pass or failures are precisely documented;
- branch targets and PR dependencies are correct;
- no temporary files or unrelated working-tree content entered a branch;
- remote child refs match local heads;
- all PR links are reciprocal and the original PR clearly acts as the umbrella;
- the original PR remains unmerged/open unless the user explicitly requested otherwise.

Report created branches/PRs, topology, validation, equivalence evidence, CI state, preserved local files, and remaining merge-order or rollout risks.
