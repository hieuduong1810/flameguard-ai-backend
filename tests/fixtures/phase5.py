from decimal import Decimal
from uuid import UUID

from app.integrations.scenario_evidence.classifications import CLASSIFICATION_VERSION
from app.integrations.scenario_evidence.models import (
    AssociationRecord,
    ProviderRequest,
    RunEvidence,
)
from app.integrations.scenario_evidence.rankings import FIXTURE_COLLECTION, FIXTURE_DATASET
from app.integrations.scenario_evidence.run_policy import MAPPING_VERSION, POLICY_VERSION
from app.schemas.api.scenarios import (
    Bindings,
    EvidenceContext,
    InvestigationIdentity,
    OriginalCondition,
    RunIdentity,
    ScenarioInput,
)
from app.services.demo_manifest import fixture_rows
from app.services.scenario_interpretation import SCENARIO_MAPPING_VERSION, interpret

COLLECTION = FIXTURE_COLLECTION
RUN = UUID(int=101)
OTHER_RUN = UUID(int=102)
INVESTIGATION = UUID("e1a75331-3f1f-57b8-9042-405ff61dff51")
OTHER_INVESTIGATION = UUID("afa58280-0d0c-58a3-926a-1499a1e20a96")
SCENARIO = {
    "name": "TEST_ONLY zero gravity",
    "environmentLabel": "fixture",
    "material": {"key": "TEST_MATERIAL_A"},
    "gravity": {"value": "0.00", "unit": "g"},
    "oxygen": {"value": "21", "unit": "%", "meaning": "ambient_oxygen_fraction_percent"},
    "pressure": {"value": "14.7", "unit": "psia"},
    "airflow": {"value": "0", "unit": "cm/s"},
}
CONDITIONS = (
    ("TEST_ONLY_GRAVITY", Decimal("0.00"), None, "g"),
    ("TEST_ONLY_MATERIAL", None, "TEST_MATERIAL_A", None),
    ("TEST_ONLY_AMBIENT_OXYGEN", Decimal("21"), None, "%"),
    ("TEST_ONLY_ABSOLUTE_PRESSURE", Decimal("14.7"), None, "psia"),
    ("TEST_ONLY_AIRFLOW", Decimal("0"), None, "cm/s"),
)
IDENTITIES = (
    InvestigationIdentity(
        investigation_id=INVESTIGATION,
        psi_id="SYNTHETIC-PHASE4-1",
        slug="synthetic-study-1",
    ),
    InvestigationIdentity(
        investigation_id=OTHER_INVESTIGATION,
        psi_id="SYNTHETIC-PHASE4-2",
        slug="synthetic-study-2",
    ),
)


def run_evidence(run_id=RUN, conditions=CONDITIONS, *, complete=True):
    return RunEvidence(
        RunIdentity(
            run_id=run_id,
            external_run_key="TEST_ONLY_RUN",
            investigation=IDENTITIES[0],
            material_type="TEST_MATERIAL_A",
            sample_geometry="TEST_ONLY inverse flame",
            gravity=None,
        ),
        tuple(
            OriginalCondition(
                condition_id=UUID(int=run_id.int * 100 + index),
                run_id=run_id,
                variable=variable,
                value_numeric=numeric,
                value_text=text,
                unit=unit,
                data_status="TEST_ONLY",
            )
            for index, (variable, numeric, text, unit) in enumerate(conditions, 1)
        ),
        complete,
    )


def provider_request(scenario=None, pillar=None):
    scenario = ScenarioInput.model_validate(SCENARIO if scenario is None else scenario)
    return ProviderRequest(
        Bindings(
            scenarioDigest=interpret(scenario).digest,
            collectionFingerprint="1" * 64,
            collectionId=FIXTURE_COLLECTION,
            datasetVersion=FIXTURE_DATASET,
            identityVersion="TEST_ONLY_slugs-v1",
            scenarioMappingVersion=SCENARIO_MAPPING_VERSION,
            mappingVersion=MAPPING_VERSION,
            ruleVersion=POLICY_VERSION,
            classificationVersion=CLASSIFICATION_VERSION,
            pillar=pillar,
        ),
        scenario,
        EvidenceContext(
            collection_id=FIXTURE_COLLECTION,
            origin="synthetic",
            review_state="unreviewed",
            caveats=("TEST_ONLY engineering fixture",),
        ),
    )


def original_associations():
    tables = fixture_rows()["tables"]
    claims = {item["id"]: item for item in tables["evidence_claim"]}
    documents = {item["id"]: item for item in tables["source_document"]}
    runs = {item["id"]: item for item in tables["test_run"]}
    result = []
    for link in sorted(tables["claim_source"], key=lambda item: item["id"]):
        claim, source = claims[link["claim_id"]], documents[link["source_document_id"]]
        result.append(
            AssociationRecord(
                association_id=link["id"],
                claim_id=claim["id"],
                claim_text=claim["claim_text"],
                evidence_status=claim["evidence_status"],
                review_status=claim["review_status"],
                limitation=claim["limitation"],
                source_document_id=source["id"],
                investigation_id=source["investigation_id"],
                source_url=source["source_url"],
                doi=source["doi"],
                document_type=source["document_type"],
                document_version=source["version"],
                ingestion_status=source["ingestion_status"],
                test_run_id=link["test_run_id"],
                run_investigation_id=runs.get(link["test_run_id"], {}).get("investigation_id"),
                source_locator=link["source_locator"],
                source_excerpt=link["source_excerpt"],
            )
        )
    return tuple(result)
