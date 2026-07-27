import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class MaintenanceCategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None
    is_active: bool = True


class MaintenanceCategoryCreate(MaintenanceCategoryBase):
    pass


class MaintenanceCategoryResponse(MaintenanceCategoryBase):
    category_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MaintenancePhotoBase(BaseModel):
    request_id: uuid.UUID
    file_path: str


class MaintenancePhotoResponse(MaintenancePhotoBase):
    photo_id: uuid.UUID
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MaintenanceRequestBase(BaseModel):
    lease_id: Optional[uuid.UUID] = None
    unit_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    status: str = "OPEN"
    assigned_to: Optional[str] = None
    cost_estimate: Optional[float] = None
    final_cost: Optional[float] = None
    currency_code: Optional[str] = None


class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass


class MaintenanceRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    completed_at: Optional[datetime] = None
    cost_estimate: Optional[float] = None
    final_cost: Optional[float] = None
    currency_code: Optional[str] = None


class MaintenanceRequestResponse(MaintenanceRequestBase):
    request_id: uuid.UUID
    reported_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
