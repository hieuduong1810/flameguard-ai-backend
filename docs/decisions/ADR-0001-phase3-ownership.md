# ADR-0001: Split Phase 3 ownership between Data and Backend

- **Status:** Accepted by project owner on 2026-11-10 as part of Codex handoff.
- **Context:** The original eight-phase backend roadmap labels Phase 3
  "Scientific ingestion and source validation". The user confirmed a
  separate Data team already owns actual NASA data collection/cleaning/import.
- **Decision:** Keep Phase 3 as a dependency/milestone, but split delivery:
  **3A Data ingestion/curation/import = Data team**, **3B Data handoff contract,
  schema validation and integration acceptance = Backend/Codex**.
- **Consequences:** The backend may implement safe acceptance tests, read-only
  queries and HTTP contracts against synthetic fixtures independently. It
  must not rebuild the Data team's pipeline or treat frontend mock fixtures as
  reviewed NASA records. Scientific API aggregates and evidence outputs are
  gated by the necessary validated source data.
- **References:** `../team-ownership.md`, `../contracts/data-handoff.md`,
  `../backend-implementation-plan.md` D12/D13 and roadmap.
- **Out of scope:** This ADR does not change the ERD, add columns, seed data,
  authorize migration/deployment, or reassign RAG/predictive work away from AI.
