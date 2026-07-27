import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InspectionBase(BaseModel):
    lease_id: Optional[uuid.UUID] = None
    unit_id: uuid.UUID
    inspection_type: str
    scheduled_date: date
    conducted_date: Optional[datetime] = None
    conducted_by: Optional[str] = None
    tenant_present: Optional[bool] = None
    overall_condition: Optional[str] = None
    condition_notes: Optional[str] = None
    damages_noted: Optional[str] = None


class InspectionCreate(InspectionBase):
    pass


class InspectionUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    conducted_date: Optional[datetime] = None
    conducted_by: Optional[str] = None
    tenant_present: Optional[bool] = None
    overall_condition: Optional[str] = None
    condition_notes: Optional[str] = None
    damages_noted: Optional[str] = None


class InspectionResponse(InspectionBase):
    inspection_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
