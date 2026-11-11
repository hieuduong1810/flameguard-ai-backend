# ADR-0002: Spec Kit adoption and canonical diagram location

- Status: Accepted for this maintenance scope by the project owner
- Date: 2026-11-11

## Context and authorization

After the read-only audit, the owner authorized updating all diagram references,
resolving adoption risks, committing the work and merging into local main.
The owner restored ADR-0001; its ownership decision remains unchanged.

## Decision

- Move the canonical HTML and its 15 faithful Mermaid exports from `docs/` to
  `docs/diagram/`. Update documentation, tests and the export utility together.
  Preserve HTML bytes and Mermaid content; do not redesign architecture or ERD.
- Retain `docs/constitution-draft.md` as historical preparation input and retain
  ADR-0001. The adopted Constitution lives in `.specify/memory/constitution.md`.
- Commit shared Spec Kit skills, templates, scripts, manifests and workflow;
  exclude secrets, environments and machine-specific generated configuration.
- Require proportionate tests for behavior changes. Use explicit manual Clarify,
  Analyze, Test and Converge evidence gates around the workflow's core commands.
  Missing required checks prevent completion; approval is not execution evidence.
- Preserve upstream integration fingerprints for update conflict detection;
  document intentional template/workflow customizations in the adoption runbook.

## Consequences and limits

README and the implementation plan receive path corrections only. No application
logic, SQLAlchemy model, migration, database data, frontend or Phase 3 feature is
changed. D01/D02's historical React/Vite labels remain design references; the
existing backend and actual Next.js consumer define the implementation boundary.
Open Data/AI/API contracts still require their owners' agreement. This decision
does not authorize scientific claims, cross-team implementation or a remote push.
