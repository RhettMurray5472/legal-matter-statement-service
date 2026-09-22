from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class DeadlineState(StrEnum):
    OVERDUE = "overdue"
    DUE_SOON = "due_soon"
    SCHEDULED = "scheduled"
    COMPLETE = "complete"


class MatterIntake(BaseModel):
    matter_id: str = Field(min_length=1, max_length=80)
    client_reference: str = Field(min_length=1, max_length=80)
    opened_on: date
    practice_area: str = Field(min_length=1, max_length=120)


class SignedDelivery(BaseModel):
    document_label: str = Field(min_length=1, max_length=120)
    signed_on: date
    delivered_on: date


class Deadline(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    due_on: date
    completed_on: date | None = None


class AccountEntry(BaseModel):
    posted_on: date
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal


class StatementRequest(BaseModel):
    matter: MatterIntake
    signed_delivery: SignedDelivery
    deadline: Deadline
    entries: list[AccountEntry] = Field(min_length=1)
    as_of_date: date


class FollowUp(BaseModel):
    state: DeadlineState
    action_required: bool


class StatementExport(BaseModel):
    matter_id: str
    follow_up: FollowUp
    pdf: dict[str, object]
