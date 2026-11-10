"""Create 0003_could_have approved ERD tables; no seed data or scientific defaults."""

import sqlalchemy as sa

from alembic import op

revision = "0003_could_have"
down_revision = "0002_should_have"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_version",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("validation_status", sa.Text(), nullable=False),
        sa.Column("applicability_domain", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_model_version"),
    )
    op.create_table(
        "model_training_run",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("model_version_id", sa.UUID(), nullable=False),
        sa.Column("training_dataset_ref", sa.Text(), nullable=False),
        sa.Column("metrics_ref", sa.Text(), nullable=True),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_model_training_run"),
        sa.ForeignKeyConstraint(
            ["model_version_id"],
            ["model_version.id"],
            name="fk_model_training_run_model_version_id_model_version",
        ),
    )
    op.create_index(
        "ix_model_training_run_model_version_id",
        "model_training_run",
        ["model_version_id"],
        unique=False,
    )
    op.create_table(
        "prediction_result",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scenario_id", sa.UUID(), nullable=False),
        sa.Column("model_version_id", sa.UUID(), nullable=False),
        sa.Column("predicted_observable", sa.Text(), nullable=False),
        sa.Column("predicted_value", sa.Numeric(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("uncertainty", sa.Numeric(), nullable=True),
        sa.Column("applicability_status", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_prediction_result"),
        sa.ForeignKeyConstraint(
            ["scenario_id"], ["scenario.id"], name="fk_prediction_result_scenario_id_scenario"
        ),
        sa.ForeignKeyConstraint(
            ["model_version_id"],
            ["model_version.id"],
            name="fk_prediction_result_model_version_id_model_version",
        ),
    )
    op.create_index(
        "ix_prediction_result_scenario_id", "prediction_result", ["scenario_id"], unique=False
    )
    op.create_index(
        "ix_prediction_result_model_version_id",
        "prediction_result",
        ["model_version_id"],
        unique=False,
    )
    op.create_table(
        "ingestion_job",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_uri", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_ingestion_job"),
    )
    op.create_table(
        "import_issue",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ingestion_job_id", sa.UUID(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("field_name", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("review_status", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_import_issue"),
        sa.ForeignKeyConstraint(
            ["ingestion_job_id"],
            ["ingestion_job.id"],
            name="fk_import_issue_ingestion_job_id_ingestion_job",
        ),
    )
    op.create_index(
        "ix_import_issue_ingestion_job_id", "import_issue", ["ingestion_job_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_import_issue_ingestion_job_id", table_name="import_issue")
    op.drop_table("import_issue")
    op.drop_table("ingestion_job")
    op.drop_index("ix_prediction_result_scenario_id", table_name="prediction_result")
    op.drop_index("ix_prediction_result_model_version_id", table_name="prediction_result")
    op.drop_table("prediction_result")
    op.drop_index("ix_model_training_run_model_version_id", table_name="model_training_run")
    op.drop_table("model_training_run")
    op.drop_table("model_version")
