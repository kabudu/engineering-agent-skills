# PR Decomposition Playbook

Read this reference when analysing boundaries or carrying out an approved split.

## Natural Breakpoint Heuristics

Strong boundaries usually align with one or more of:

- domain capability or user-visible workflow;
- architectural layer with a stable contract;
- schema/model foundation followed by consumers;
- reusable infrastructure followed by product adoption;
- read path followed by write path only when each is useful and safe alone;
- backend/API contract followed by UI integration;
- generic platform capability followed by customer-specific setup;
- operational tooling, migrations, or documentation that can be reviewed with the behaviour it enables.

Weak boundaries include arbitrary directories, equal line counts, chronological batches with mixed purposes, tests detached from implementation, and refactors mixed with unrelated product behaviour.

## Dependency Classification

For every candidate slice, classify dependencies as:

- **Compile/load:** symbols, generated accessors, autoload mappings, assets, templates.
- **Data:** schema, migrations, seeds, backfills, serialization formats.
- **Behaviour:** callers rely on a new invariant or changed semantics.
- **Operational:** configuration defaults, cron/queue workers, deployment ordering, feature flags.
- **Review:** understanding the slice requires context that only exists in another slice.

If a dependency is required at runtime or for validation, model it in the branch topology. A prose note cannot make an unsafe sibling PR independent.

## Candidate Slice Test

A useful slice should answer yes to most of these:

1. Does it have one sentence explaining its purpose?
2. Can a reviewer understand its contract from this diff and declared prerequisites?
3. Does it leave its target branch buildable and operationally safe?
4. Can its behaviour be tested meaningfully at this stage?
5. Could it be reverted without silently corrupting later slices?
6. Is its migration/configuration ordering explicit?
7. Does it avoid duplicating code that will be removed by a later slice?

Merge candidates that fail because they are artificially narrow. Stack them when the dependency is real but the review boundary remains valuable.

## Typical Series Shapes

### Foundation then capabilities

1. Shared schema/contracts/generated models.
2. Core services and persistence.
3. API/admin integration.
4. UI and operator workflow.
5. Customer-specific configuration or migration.

Use only the levels present in the changeset; do not manufacture a five-PR stack.

### Independent capabilities

- Capability A targets the original base.
- Capability B targets the original base.
- Shared foundation becomes a small prerequisite PR only when both genuinely require it.

### Refactor plus behaviour

Put a behaviour-preserving refactor first only when it materially simplifies review and has strong regression coverage. Otherwise keep the refactor with the behaviour that justifies it.

## Equivalence Proof

Use more than path accounting:

- compare the reconstructed final tree to the original head;
- explain intentional metadata differences such as PR-only changelog/link edits;
- inventory original commits and cross-cutting hunks;
- verify migrations and generated outputs are neither duplicated nor omitted;
- run the original branch's focused/full validation on the reconstructed final stack;
- inspect aggregate diff statistics and important configuration defaults.

Exact tree equality is preferred when the task is purely decomposition. If cleanup changes are useful, keep them separate and obtain approval rather than silently folding them into the split.

## PR Linking Template

Each child PR should state:

- `Part N of M of #<umbrella>`;
- purpose and review boundary;
- base/dependency and required merge order;
- what is deliberately deferred to later parts;
- tests/checks run;
- whether it is independently deployable.

The umbrella should list all child PRs in order with status and dependencies. Do not imply that GitHub will retarget stacked children automatically; verify bases after each merge.

## Failure and Change Handling

- If the original head moves, stop mutation, fetch, and refresh the plan/equivalence proof.
- If a child cannot pass validation without later work, combine it or make the dependency explicit through stacking.
- If branch protection or permissions prevent creation/linking, leave local refs intact and report the exact blocker.
- If CI changes the dependency picture, revise links and merge order before continuing.
- Never close the umbrella merely because child PRs exist; that is a separate product/review decision.
