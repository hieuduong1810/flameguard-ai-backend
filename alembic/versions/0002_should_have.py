"""Create 0002_should_have approved ERD tables; no seed data or scientific defaults."""

import sqlalchemy as sa

from alembic import op

revision = "0002_should_have"
down_revision = "0001_must_have"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tag",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_tag"),
        sa.UniqueConstraint("slug", name="uq_tag_slug"),
    )
    op.create_table(
        "investigation_tag",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("investigation_id", sa.UUID(), nullable=False),
        sa.Column("tag_id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_investigation_tag"),
        sa.ForeignKeyConstraint(
            ["investigation_id"],
            ["investigation.id"],
            name="fk_investigation_tag_investigation_id_investigation",
        ),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], name="fk_investigation_tag_tag_id_tag"),
    )
    op.create_index(
        "ix_investigation_tag_investigation_id",
        "investigation_tag",
        ["investigation_id"],
        unique=False,
    )
    op.create_index("ix_investigation_tag_tag_id", "investigation_tag", ["tag_id"], unique=False)
    op.create_table(
        "match_dimension",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scenario_match_id", sa.UUID(), nullable=False),
        sa.Column("variable", sa.Text(), nullable=False),
        sa.Column("match_status", sa.Text(), nullable=False),
        sa.Column("gap_reason", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_match_dimension"),
        sa.ForeignKeyConstraint(
            ["scenario_match_id"],
            ["scenario_match.id"],
            name="fk_match_dimension_scenario_match_id_scenario_match",
        ),
    )
    op.create_index(
        "ix_match_dimension_scenario_match_id",
        "match_dimension",
        ["scenario_match_id"],
        unique=False,
    )
    op.create_table(
        "document_chunk",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_document_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("source_locator", sa.Text(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding_ref", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_document_chunk"),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_document.id"],
            name="fk_document_chunk_source_document_id_source_document",
        ),
    )
    op.create_index(
        "ix_document_chunk_source_document_id",
        "document_chunk",
        ["source_document_id"],
        unique=False,
    )
    op.create_table(
        "chat_session",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("investigation_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_chat_session"),
        sa.ForeignKeyConstraint(
            ["investigation_id"],
            ["investigation.id"],
            name="fk_chat_session_investigation_id_investigation",
        ),
    )
    op.create_index(
        "ix_chat_session_investigation_id", "chat_session", ["investigation_id"], unique=False
    )
    op.create_table(
        "chat_message",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("chat_session_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_chat_message"),
        sa.ForeignKeyConstraint(
            ["chat_session_id"],
            ["chat_session.id"],
            name="fk_chat_message_chat_session_id_chat_session",
        ),
    )
    op.create_index(
        "ix_chat_message_chat_session_id", "chat_message", ["chat_session_id"], unique=False
    )
    op.create_table(
        "message_citation",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("chat_message_id", sa.UUID(), nullable=False),
        sa.Column("source_document_id", sa.UUID(), nullable=False),
        sa.Column("source_locator", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_message_citation"),
        sa.ForeignKeyConstraint(
            ["chat_message_id"],
            ["chat_message.id"],
            name="fk_message_citation_chat_message_id_chat_message",
        ),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_document.id"],
            name="fk_message_citation_source_document_id_source_document",
        ),
    )
    op.create_index(
        "ix_message_citation_chat_message_id", "message_citation", ["chat_message_id"], unique=False
    )
    op.create_index(
        "ix_message_citation_source_document_id",
        "message_citation",
        ["source_document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_message_citation_chat_message_id", table_name="message_citation")
    op.drop_index("ix_message_citation_source_document_id", table_name="message_citation")
    op.drop_table("message_citation")
    op.drop_index("ix_chat_message_chat_session_id", table_name="chat_message")
    op.drop_table("chat_message")
    op.drop_index("ix_chat_session_investigation_id", table_name="chat_session")
    op.drop_table("chat_session")
    op.drop_index("ix_document_chunk_source_document_id", table_name="document_chunk")
    op.drop_table("document_chunk")
    op.drop_index("ix_match_dimension_scenario_match_id", table_name="match_dimension")
    op.drop_table("match_dimension")
    op.drop_index("ix_investigation_tag_investigation_id", table_name="investigation_tag")
    op.drop_index("ix_investigation_tag_tag_id", table_name="investigation_tag")
    op.drop_table("investigation_tag")
    op.drop_table("tag")
