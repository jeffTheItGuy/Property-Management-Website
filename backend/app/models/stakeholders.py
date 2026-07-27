import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, Boolean, DateTime, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Landlord(Base):
    __tablename__ = "landlords"

    landlord_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(200))
    national_id: Mapped[str] = mapped_column(String(50), unique=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bank_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    properties: Mapped[List["Property"]] = relationship(back_populates="landlord")


class PropertyManager(Base):
    __tablename__ = "property_managers"

    manager_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(200))
    national_id: Mapped[str] = mapped_column(String(50), unique=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    commission_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    properties: Mapped[List["Property"]] = relationship(back_populates="manager")


class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(200))
    national_id: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employer_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    monthly_income: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    guarantors: Mapped[List["TenantGuarantor"]] = relationship(back_populates="tenant")
    lease_tenants: Mapped[List["LeaseTenant"]] = relationship(back_populates="tenant")


class TenantGuarantor(Base):
    __tablename__ = "tenant_guarantors"

    guarantor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"))
    full_name: Mapped[str] = mapped_column(String(200))
    national_id: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20))
    relationship_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tenant: Mapped["Tenant"] = relationship(back_populates="guarantors")