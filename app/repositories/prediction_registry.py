from uuid import UUID

from sqlalchemy import select

from app.models.prediction import ModelTrainingRun, ModelVersion


async def model_record(session, model_id: UUID):
    row = (
        await session.execute(select(ModelVersion).where(ModelVersion.id == model_id))
    ).scalar_one_or_none()
    if row is None:
        return None
    return {
        key: getattr(row, key)
        for key in ("id", "version", "validation_status", "applicability_domain")
    }


async def training_record(session, model_id: UUID, training_id: UUID):
    row = (
        await session.execute(
            select(ModelTrainingRun).where(
                ModelTrainingRun.id == training_id, ModelTrainingRun.model_version_id == model_id
            )
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    return {key: getattr(row, key) for key in ("training_dataset_ref", "metrics_ref")}
