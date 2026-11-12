import json
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, StringConstraints

from app.integrations.scenario_evidence.execution import (
    MAX_ENTRIES,
    ProviderFailure,
    decode,
    reject,
)
from app.integrations.scenario_evidence.models import AssociationRecord, ProviderRequest
from app.schemas.api.scenarios import Fingerprint, Pillar, WireInput

CLASSIFICATION_VERSION = "TEST_ONLY_claim-classification-v1"
CLAIM_ID = UUID("1dc0b6db-25b6-5438-9322-ec1d4cf35f58")
REFERENCE_ROWS = (
    ("63371883-7b34-5688-b4f7-fd40d13e0e7f", "d0127a19-6b2a-5186-8dd6-8ffb213832c2", 0),
    ("8d3ee8d5-3a05-5bad-b86a-3d4529ea23f8", "d0127a19-6b2a-5186-8dd6-8ffb213832c2", 1),
    ("433f8940-2f71-5bf0-b63c-6d5df22c1fc6", "19350546-1534-5b0c-adaf-bd6bdd84fa01", 2),
    ("d786824b-55ff-5458-b5ae-7df3b9f7a8e3", "a2c85b1f-c4cb-588a-b992-83d4cce9ebf3", 3),
)
UUIDText = Annotated[str, StringConstraints(min_length=32, max_length=45)]
LocatorText = Annotated[str, StringConstraints(min_length=1, max_length=2000)]


class SourceReference(WireInput):
    association_id: UUIDText
    claim_id: UUIDText
    document_id: UUIDText
    locator: LocatorText
    pillar: Pillar


class Classification(WireInput):
    version: Literal[CLASSIFICATION_VERSION]
    collection_fingerprint: Fingerprint
    scenario_digest: Fingerprint
    origin: Literal["synthetic"]
    review_state: Literal["unreviewed"]
    references: Annotated[list[SourceReference], Field(max_length=MAX_ENTRIES)]


class FixedClassification:
    version = CLASSIFICATION_VERSION
    claim_ids = (CLAIM_ID,)

    async def classify(self, request: ProviderRequest, associations: tuple[AssociationRecord, ...]):
        return json.dumps(
            {
                "version": self.version,
                "collectionFingerprint": request.scope.collection_fingerprint,
                "scenarioDigest": request.scope.scenario_digest,
                "origin": "synthetic",
                "reviewState": "unreviewed",
                "references": [
                    {
                        "associationId": association,
                        "claimId": str(CLAIM_ID),
                        "documentId": document,
                        "locator": f"TEST_ONLY locator {locator}",
                        "pillar": "prevention",
                    }
                    for association, document, locator in REFERENCE_ROWS
                ],
            }
        ).encode()


def validate_classification(
    payload: bytes,
    request: ProviderRequest,
    associations: tuple[AssociationRecord, ...],
) -> dict[UUID, Pillar]:
    if not request.test_only:
        raise reject()
    delivery = decode(payload, Classification)
    if (
        delivery.version != request.scope.classification_version
        or delivery.collection_fingerprint != request.scope.collection_fingerprint
        or delivery.scenario_digest != request.scope.scenario_digest
    ):
        raise ProviderFailure("PROVIDER_VERSION_CONFLICT", rejected=True)

    known = {item.association_id: item for item in associations}
    selected = {}
    claim_pillars = {}
    for ref in delivery.references:
        try:
            uid, claim, document = map(UUID, (ref.association_id, ref.claim_id, ref.document_id))
        except ValueError:
            raise reject() from None
        record = known.get(uid)
        if (
            record is None
            or record.claim_id != claim
            or record.source_document_id != document
            or record.source_locator != ref.locator
        ):
            raise ProviderFailure("SOURCE_MAPPING_UNRESOLVED", rejected=True)
        if uid in selected or claim_pillars.setdefault(claim, ref.pillar) != ref.pillar:
            raise reject()
        selected[uid] = ref.pillar
    if selected.keys() != known.keys():
        raise ProviderFailure("SOURCE_MAPPING_UNRESOLVED", rejected=True)
    return selected
