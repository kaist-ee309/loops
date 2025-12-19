from datetime import datetime

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Return current UTC time as naive datetime (for PostgreSQL TIMESTAMP WITHOUT TIME ZONE)."""
    return datetime.utcnow()


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(
        default_factory=utc_now,
        nullable=False,
        sa_column_kwargs={"onupdate": utc_now},
    )
