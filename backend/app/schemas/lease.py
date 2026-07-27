import uuid
from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class LeaseTenantBase(BaseModel):
    lease_id: uuid.UUID
    tenant_id: uuid.UUID
    is_primary: bool = False


class LeaseTenantCreate(LeaseTenantBase):
    pass


class LeaseTenantResponse(LeaseTenantBase):
    lease_tenant_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LeaseDocumentBase(BaseModel):
    lease_id: uuid.UUID
    document_type: str
    file_path: str
    signed_at: Optional[datetime] = None


class LeaseDocumentCreate(LeaseDocumentBase):
    pass


class LeaseDocumentResponse(LeaseDocumentBase):
    doc_id: uuid.UUID
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LeaseBase(BaseModel):
    lease_number: str
    unit_id: uuid.UUID
    primary_tenant_id: uuid.UUID
    start_date: date
    end_date: date
    base_rent: float
    rent_currency: str = "USD"
    deposit_amount: float
    payment_due_day: int = 1
    late_fee_amount: Optional[float] = None
    includes_water: bool = False
    includes_zesa: bool = False
    includes_rates: bool = False
    rent_review_date: Optional[date] = None
    escalation_notes: Optional[str] = None
    status: str = "DRAFT"
    notes: Optional[str] = None


class LeaseCreate(LeaseBase):
    pass


class LeaseUpdate(BaseModel):
    lease_number: Optional[str] = None
    unit_id: Optional[uuid.UUID] = None
    primary_tenant_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    base_rent: Optional[float] = None
    rent_currency: Optional[str] = None
    deposit_amount: Optional[float] = None
    payment_due_day: Optional[int] = None
    late_fee_amount: Optional[float] = None
    includes_water: Optional[bool] = None
    includes_zesa: Optional[bool] = None
    includes_rates: Optional[bool] = None
    rent_review_date: Optional[date] = None
    escalation_notes: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class LeaseResponse(LeaseBase):
    lease_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)