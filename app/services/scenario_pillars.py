from app.integrations.scenario_evidence.classifications import validate_classification
from app.integrations.scenario_evidence.execution import ProviderFailure, execute
from app.integrations.scenario_evidence.models import AssociationRecord, ProviderRequest
from app.integrations.scenario_evidence.protocols import ClassificationProvider
from app.schemas.api.scenarios import (
    PILLARS,
    EvaluationRequest,
    FixtureLabel,
    OriginalClaim,
    OriginalDocument,
    Pillar,
    PillarAssociation,
    PillarEvidence,
    PillarGroup,
)
from app.services.scenario_interpretation import fingerprint
from app.services.scenario_traversal import page_for


def project(row: AssociationRecord, pillar: Pillar, label: FixtureLabel) -> PillarAssociation:
    reasons = ["TEST_ONLY_UNREVIEWED"]
    if row.test_run_id is None:
        reasons.append("RUN_CONTEXT_MISSING")
    elif row.run_investigation_id != row.investigation_id:
        reasons.append("SOURCE_RUN_CONTEXT_MISMATCH")
    return PillarAssociation(
        association_id=row.association_id,
        pillar=pillar,
        context=label,
        reason_codes=tuple(reasons),
        claim=OriginalClaim(
            claim_id=row.claim_id,
            claim_text=row.claim_text,
            evidence_status=row.evidence_status,
            review_status=row.review_status,
            limitation=row.limitation,
            context=label,
        ),
        document=OriginalDocument(
            source_document_id=row.source_document_id,
            investigation_id=row.investigation_id,
            source_url=row.source_url,
            doi=row.doi,
            document_type=row.document_type,
            version=row.document_version,
            ingestion_status=row.ingestion_status,
            context=label,
        ),
        test_run_id=row.test_run_id,
        run_investigation_id=row.run_investigation_id,
        source_locator=row.source_locator,
        source_excerpt=row.source_excerpt,
    )


async def pillar_section(
    provider: ClassificationProvider | None,
    provider_request: ProviderRequest,
    request: EvaluationRequest,
    associations: tuple[AssociationRecord, ...] | None,
) -> tuple[PillarEvidence, str | None]:
    scope = provider_request.scope
    if provider is None:
        return PillarEvidence(
            state="unavailable", reason_codes=("CLASSIFICATION_UNAVAILABLE",)
        ), None
    if associations is None:
        return PillarEvidence(
            state="unavailable", reason_codes=("ASSOCIATION_LIMIT_EXCEEDED",)
        ), None
    try:
        payload = await execute(provider.classify(provider_request, associations))
        mapping = validate_classification(payload, provider_request, associations)
    except ProviderFailure as exc:
        return PillarEvidence(
            state="rejected" if exc.rejected else "unavailable",
            reason_codes=(exc.code,),
        ), None
    digest = fingerprint({str(identity): pillar for identity, pillar in mapping.items()})
    scope = scope.model_copy(update={"classification_fingerprint": digest})
    label = FixtureLabel(
        collection_id=scope.collection_id,
        dataset_version=scope.dataset_version,
        provider_version=provider.version,
    )
    selected = (request.pillar,) if request.pillar else PILLARS
    rows = tuple(
        (row, mapping[row.association_id])
        for row in associations
        if mapping[row.association_id] in selected
    )
    page = page_for(request, scope, "evidence_offset", len(rows))
    items = tuple(
        project(row, pillar, label) for row, pillar in rows[page.offset : page.offset + page.limit]
    )
    groups = []
    for pillar in selected:
        group_items = tuple(item for item in items if item.pillar == pillar)
        total = sum(p == pillar for _, p in rows)
        reasons = ()
        if not total:
            reasons = ("NO_CLASSIFIED_ASSOCIATIONS_IN_SCOPE",)
        elif not group_items:
            reasons = ("ASSOCIATIONS_OUTSIDE_EXAMINED_PAGE",)
        groups.append(
            PillarGroup(
                pillar=pillar,
                total=total,
                items=group_items,
                reason_codes=reasons,
                context=label,
            )
        )
    return PillarEvidence(
        state="evaluated", reason_codes=(), groups=tuple(groups), page=page
    ), digest
