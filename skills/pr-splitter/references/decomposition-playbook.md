# PR Decomposition Playbook

Use these heuristics and examples when boundary decisions need additional guidance. The entry point defines authorization, execution, changelog, equivalence, linking, and completion requirements.

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

Use these questions to apply the entry point’s safety and review requirements:

1. Does it have one sentence explaining its purpose?
2. Can a reviewer understand its contract from this diff and declared prerequisites?
3. Does it leave its target branch buildable and operationally safe?
4. Can its behaviour be tested meaningfully at this stage?
5. Is its migration/configuration ordering explicit?
6. Does it avoid duplicating code that will be removed by a later slice?
7. Does its changelog describe only behaviour this slice fully delivers?

Also assess whether the slice can be reverted safely with its dependants; document any required rollback order. Prefer boundaries with simple rollback.

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

## Changelog Inspection Technique

Apply the entry point's changelog policy at planning, per-child validation, and aggregate reconstruction. Use repository-specific paths; inspect each child's additions with `git diff <actual-base>...<child> -- <changelog-paths>`, then compare the aggregate with the original head. In a stack, inherited entries are not new child entries: inspect the diff against the immediate parent.
