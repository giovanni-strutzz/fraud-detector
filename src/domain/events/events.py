from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional


class DomainEvent(BaseModel):
    event_id: UUID4
    occurred_at: datetime = Field(default_factory=datetime.now)


class RequestedTransfer(DomainEvent):
    transaction_id: UUID4
    origin_account_id: str
    destination_account_id: str
    origin_document: str
    destination_document: str
    value: float
    origin_bank_code: str
    destination_bank_code: str
    metadata: Optional[dict] = None


class ProcessedTransfer(DomainEvent):
    transaction_id: UUID4
    status: str = "PROCESSED"


class FailedTransfer(DomainEvent):
    transaction_id: UUID4
    reason: str
    status: str = "FAILED"