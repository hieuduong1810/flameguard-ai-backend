# Focused consistency analysis

Prepared 2026-11-13 from the existing backlog, prediction ORM, Phase 6 provider
and writer architecture, current admission contracts and Constitution.

| Finding | Disposition |
| --- | --- |
| API names are proposals in the backlog and readiness is TBD in the frontend contract | Concrete additive GET/POST proposal awaits owner approval. |
| Registry Text fields alone cannot prove scientific validation | Require versioned AI-owned metadata and independent data/publication acceptance. Unknown declarations keep not_ready. |
| Current scientific admission allows unreviewed/unknown collections | Keep scientific execution closed pending reviewed corpus acceptance. No implicit admission-policy relaxation. |
| Mock execution must not imply validated predictions | Fixed labeled internal provider tests; public mock/unvalidated scientific requests remain not_ready. |
| P7-06 persistence is conditional and runtime writer is chat-only | Stateless scope proposed with no-write verification. Future persistence requires explicit FK/provenance/permission impact review. |
| Rich uncertainty exceeds current scalar PredictionResult field | Retain versioned provider uncertainty metadata in stateless output; storage requires separate mapping approval. |
| Original data/model identity can drift during provider execution | Bind registry/provider/data versions and recheck admitted snapshot before returning a result. |

FR-001–FR-008 and SC-001–SC-003 map to T005–T012. T013/T014 retain external
acceptance. Ordinary implementation choices can proceed within the accepted
scope after T004. Existing Phase 6 artifacts remain the preserved baseline.
