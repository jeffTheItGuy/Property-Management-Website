import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# Landlord
class LandlordBase(BaseModel):
    full_name: str
    national_id: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    bank_details: Optional[str] = None
    is_active: bool = True


class LandlordCreate(LandlordBase):
    pass


class LandlordUpdate(BaseModel):
    full_name: Optional[str] = None
    national_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    bank_details: Optional[str] = None
    is_active: Optional[bool] = None


class LandlordResponse(LandlordBase):
    landlord_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# PropertyManager
class PropertyManagerBase(BaseModel):
    full_name: str
    national_id: str
    phone: str
    email: Optional[str] = None
    commission_rate: Optional[float] = None
    is_active: bool = True


class PropertyManagerCreate(PropertyManagerBase):
    password: str


class PropertyManagerUpdate(BaseModel):
    full_name: Optional[str] = None
    national_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    commission_rate: Optional[float] = None
    is_active: Optional[bool] = None


class PropertyManagerResponse(PropertyManagerBase):
    manager_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Tenant
class TenantBase(BaseModel):
    full_name: str
    national_id: str
    phone: str
    email: Optional[str] = None
    employer_name: Optional[str] = None
    monthly_income: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    full_name: Optional[str] = None
    national_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    employer_name: Optional[str] = None
    monthly_income: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class TenantResponse(TenantBase):
    tenant_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# TenantGuarantor
class TenantGuarantorBase(BaseModel):
    tenant_id: uuid.UUID
    full_name: str
    national_id: str
    phone: str
    relationship_type: Optional[str] = None


class TenantGuarantorCreate(TenantGuarantorBase):
    pass


class TenantGuarantorResponse(TenantGuarantorBase):
    guarantor_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)