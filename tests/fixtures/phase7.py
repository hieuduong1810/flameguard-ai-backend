from uuid import UUID

from app.schemas.api.predictions import ModelMetadata, PredictionRequest

MODEL_ID = UUID("70000000-0000-4000-8000-000000000001")
TRAINING_ID = UUID("70000000-0000-4000-8000-000000000002")


def metadata():
    return ModelMetadata(
        schema_version=1,
        artifact_ref="TEST_ONLY_artifact",
        training_run_id=TRAINING_ID,
        dataset_version="TEST_ONLY_fixture-v1",
        evaluation_ref="TEST_ONLY_evaluation",
        uncertainty_ref="TEST_ONLY_uncertainty",
        validation_expires_at="2100-01-01T00:00:00Z",
        materials=("TEST_ONLY_material",),
        gravity={"minimum": "0", "maximum": "0", "unit": "g"},
        oxygen={"minimum": "0", "maximum": "0", "unit": "%"},
        oxygen_meaning="ambient_oxygen_fraction_percent",
        pressure={"minimum": "0", "maximum": "0", "unit": "psia"},
        airflow={"minimum": "0", "maximum": "0", "unit": "cm/s"},
        observables={"TEST_ONLY_observable": "TEST_ONLY_unit"},
        limitations=("TEST_ONLY no scientific meaning",),
    )


def request_body():
    return {
        "modelId": str(MODEL_ID),
        "expectedModelVersion": "TEST_ONLY-v1",
        "expectedDatasetVersion": "TEST_ONLY_fixture-v1",
        "observable": "TEST_ONLY_observable",
        "scenario": {
            "material": {"key": "TEST_ONLY_material"},
            "gravity": {"value": "0", "unit": "g"},
            "oxygen": {"value": "0", "unit": "%", "meaning": "ambient_oxygen_fraction_percent"},
            "pressure": {"value": "0", "unit": "psia"},
            "airflow": {"value": "0", "unit": "cm/s"},
        },
    }


def request():
    return PredictionRequest.model_validate(request_body())
