from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared metadata for all approved database entities."""

    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
        }
    )


class UUIDPrimaryKey:
    """Only the ERD's shared id column; no extra audit columns are introduced."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


def utc_now() -> datetime:
    return datetime.now(UTC)
