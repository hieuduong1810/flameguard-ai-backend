"""Create 0001_must_have approved ERD tables; no seed data or scientific defaults."""

import sqlalchemy as sa

from alembic import op

revision = "0001_must_have"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "investigation",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("psi_id", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("research_purpose", sa.Text(), nullable=True),
        sa.Column("platform", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_investigation"),
        sa.UniqueConstraint("psi_id", name="uq_investigation_psi_id"),
    )
    op.create_table(
        "test_run",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("investigation_id", sa.UUID(), nullable=False),
        sa.Column("external_run_key", sa.Text(), nullable=True),
        sa.Column("material_type", sa.Text(), nullable=True),
        sa.Column("sample_geometry", sa.Text(), nullable=True),
        sa.Column("gravity", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_test_run"),
        sa.ForeignKeyConstraint(
            ["investigation_id"],
            ["investigation.id"],
            name="fk_test_run_investigation_id_investigation",
        ),
    )
    op.create_index("ix_test_run_investigation_id", "test_run", ["investigation_id"], unique=False)
    op.create_table(
        "test_condition",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("test_run_id", sa.UUID(), nullable=False),
        sa.Column("variable", sa.Text(), nullable=False),
        sa.Column("value_numeric", sa.Numeric(), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column("data_status", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_test_condition"),
        sa.ForeignKeyConstraint(
            ["test_run_id"], ["test_run.id"], name="fk_test_condition_test_run_id_test_run"
        ),
    )
    op.create_index(
        "ix_test_condition_test_run_id", "test_condition", ["test_run_id"], unique=False
    )
    op.create_table(
        "measurement",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("test_run_id", sa.UUID(), nullable=False),
        sa.Column("observable", sa.Text(), nullable=False),
        sa.Column("measured_value", sa.Numeric(), nullable=True),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("raw_asset_ref", sa.Text(), nullable=True),
        sa.Column("uncertainty", sa.Numeric(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_measurement"),
        sa.ForeignKeyConstraint(
            ["test_run_id"], ["test_run.id"], name="fk_measurement_test_run_id_test_run"
        ),
    )
    op.create_index("ix_measurement_test_run_id", "measurement", ["test_run_id"], unique=False)
    op.create_table(
        "source_document",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("investigation_id", sa.UUID(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("doi", sa.Text(), nullable=True),
        sa.Column("document_type", sa.Text(), nullable=False),
        sa.Column("version", sa.Text(), nullable=True),
        sa.Column("ingestion_status", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_source_document"),
        sa.ForeignKeyConstraint(
            ["investigation_id"],
            ["investigation.id"],
            name="fk_source_document_investigation_id_investigation",
        ),
    )
    op.create_index(
        "ix_source_document_investigation_id", "source_document", ["investigation_id"], unique=False
    )
    op.create_table(
        "evidence_claim",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("evidence_status", sa.Text(), nullable=False),
        sa.Column("review_status", sa.Text(), nullable=False),
        sa.Column("limitation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_evidence_claim"),
    )
    op.create_table(
        "claim_source",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("claim_id", sa.UUID(), nullable=False),
        sa.Column("source_document_id", sa.UUID(), nullable=False),
        sa.Column("test_run_id", sa.UUID(), nullable=True),
        sa.Column("source_locator", sa.Text(), nullable=False),
        sa.Column("source_excerpt", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_claim_source"),
        sa.ForeignKeyConstraint(
            ["claim_id"], ["evidence_claim.id"], name="fk_claim_source_claim_id_evidence_claim"
        ),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_document.id"],
            name="fk_claim_source_source_document_id_source_document",
        ),
        sa.ForeignKeyConstraint(
            ["test_run_id"], ["test_run.id"], name="fk_claim_source_test_run_id_test_run"
        ),
    )
    op.create_index("ix_claim_source_claim_id", "claim_source", ["claim_id"], unique=False)
    op.create_index(
        "ix_claim_source_source_document_id", "claim_source", ["source_document_id"], unique=False
    )
    op.create_index("ix_claim_source_test_run_id", "claim_source", ["test_run_id"], unique=False)
    op.create_table(
        "scenario",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("environment", sa.Text(), nullable=False),
        sa.Column("gravity", sa.Text(), nullable=False),
        sa.Column("oxygen_pct", sa.Numeric(), nullable=False),
        sa.Column("pressure_psi", sa.Numeric(), nullable=False),
        sa.Column("material", sa.Text(), nullable=False),
        sa.Column("ventilation", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_scenario"),
    )
    op.create_table(
        "scenario_match",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scenario_id", sa.UUID(), nullable=False),
        sa.Column("test_run_id", sa.UUID(), nullable=False),
        sa.Column("match_status", sa.Text(), nullable=False),
        sa.Column("score", sa.Numeric(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("engine_version", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_scenario_match"),
        sa.ForeignKeyConstraint(
            ["scenario_id"], ["scenario.id"], name="fk_scenario_match_scenario_id_scenario"
        ),
        sa.ForeignKeyConstraint(
            ["test_run_id"], ["test_run.id"], name="fk_scenario_match_test_run_id_test_run"
        ),
    )
    op.create_index(
        "ix_scenario_match_scenario_id", "scenario_match", ["scenario_id"], unique=False
    )
    op.create_index(
        "ix_scenario_match_test_run_id", "scenario_match", ["test_run_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_scenario_match_scenario_id", table_name="scenario_match")
    op.drop_index("ix_scenario_match_test_run_id", table_name="scenario_match")
    op.drop_table("scenario_match")
    op.drop_table("scenario")
    op.drop_index("ix_claim_source_claim_id", table_name="claim_source")
    op.drop_index("ix_claim_source_source_document_id", table_name="claim_source")
    op.drop_index("ix_claim_source_test_run_id", table_name="claim_source")
    op.drop_table("claim_source")
    op.drop_table("evidence_claim")
    op.drop_index("ix_source_document_investigation_id", table_name="source_document")
    op.drop_table("source_document")
    op.drop_index("ix_measurement_test_run_id", table_name="measurement")
    op.drop_table("measurement")
    op.drop_index("ix_test_condition_test_run_id", table_name="test_condition")
    op.drop_table("test_condition")
    op.drop_index("ix_test_run_investigation_id", table_name="test_run")
    op.drop_table("test_run")
    op.drop_table("investigation")
