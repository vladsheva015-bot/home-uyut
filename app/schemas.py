from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Source(StrEnum):
    SITE = "site"
    AVITO = "avito"
    TELEGRAM = "telegram"


class Priority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LeadCreate(BaseModel):
    source: Source
    text: str = Field(min_length=1)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    created_at: datetime | None = None

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: Source
    text: str
    amount: Decimal | None
    created_at: datetime
    priority: Priority
