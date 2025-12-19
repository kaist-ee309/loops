"""Schemas for Favorite model."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class FavoriteCreate(SQLModel):
    """Schema for creating a favorite."""

    card_id: int = Field(gt=0, description="Card ID must be positive")


class FavoriteRead(SQLModel):
    """Schema for reading a favorite."""

    id: int
    user_id: UUID
    card_id: int
    created_at: datetime
    updated_at: datetime | None = None
