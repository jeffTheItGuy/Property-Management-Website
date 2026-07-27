import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaymentScheduleBase(BaseModel):
    lease_id: uuid.UUID
    due_date: date
    amount_due: float
    currency_code: str = "USD"
    description: Optional[str] = None
    status: str = "PENDING"


class PaymentScheduleCreate(PaymentScheduleBase):
    pass


class PaymentScheduleUpdate(BaseModel):
    due_date: Optional[date] = None
    amount_due: Optional[float] = None
    currency_code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PaymentScheduleResponse(PaymentScheduleBase):
    schedule_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RentPaymentBase(BaseModel):
    lease_id: uuid.UUID
    schedule_id: Optional[uuid.UUID] = None
    payment_method: str
    currency_code: str
    amount_paid: float
    reference_number: Optional[str] = None
    receipt_number: str
    period_from: date
    period_to: date
    received_by: Optional[uuid.UUID] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None


class RentPaymentCreate(RentPaymentBase):
    pass


class RentPaymentResponse(RentPaymentBase):
    payment_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DepositBase(BaseModel):
    lease_id: uuid.UUID
    amount: float
    currency_code: str
    held_by: str = "LANDLORD"
    status: str = "HELD"
    deductions_amount: Optional[float] = None
    deductions_reason: Optional[str] = None
    returned_amount: Optional[float] = None
    returned_at: Optional[datetime] = None


class DepositCreate(DepositBase):
    pass


class DepositUpdate(BaseModel):
    status: Optional[str] = None
    deductions_amount: Optional[float] = None
    deductions_reason: Optional[str] = None
    returned_amount: Optional[float] = None
    returned_at: Optional[datetime] = None


class DepositResponse(DepositBase):
    deposit_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
