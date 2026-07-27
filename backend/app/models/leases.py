import uuid
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import String, Text, Date, DateTime, Numeric, Integer, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Lease(Base):
    __tablename__ = "leases"

    lease_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_number: Mapped[str] = mapped_column(String(50), unique=True)
    unit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("units.unit_id"))
    primary_tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    base_rent: Mapped[float] = mapped_column(Numeric(18, 2))
    rent_currency: Mapped[str] = mapped_column(String(3), default="USD")
    deposit_amount: Mapped[float] = mapped_column(Numeric(18, 2))
    payment_due_day: Mapped[int] = mapped_column(Integer, default=1)
    late_fee_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True)
    includes_water: Mapped[bool] = mapped_column(Boolean, default=False)
    includes_zesa: Mapped[bool] = mapped_column(Boolean, default=False)
    includes_rates: Mapped[bool] = mapped_column(Boolean, default=False)
    rent_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    escalation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")  # DRAFT, ACTIVE, ENDED, BREACHED
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    unit: Mapped["Unit"] = relationship(back_populates="leases")
    primary_tenant: Mapped["Tenant"] = relationship(foreign_keys=[primary_tenant_id])
    lease_tenants: Mapped[List["LeaseTenant"]] = relationship(back_populates="lease")
    documents: Mapped[List["LeaseDocument"]] = relationship(back_populates="lease")
    payment_schedules: Mapped[List["PaymentSchedule"]] = relationship(back_populates="lease")
    rent_payments: Mapped[List["RentPayment"]] = relationship(back_populates="lease")
    deposits: Mapped[List["Deposit"]] = relationship(back_populates="lease")
    maintenance_requests: Mapped[List["MaintenanceRequest"]] = relationship(back_populates="lease")
    inspections: Mapped[List["Inspection"]] = relationship(back_populates="lease")


class LeaseTenant(Base):
    __tablename__ = "lease_tenants"

    lease_tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.lease_id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lease: Mapped["Lease"] = relationship(back_populates="lease_tenants")
    tenant: Mapped["Tenant"] = relationship(back_populates="lease_tenants")


class LeaseDocument(Base):
    __tablename__ = "lease_documents"

    doc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.lease_id"))
    document_type: Mapped[str] = mapped_column(String(50))  # AGREEMENT, INVENTORY, CONDITION_REPORT
    file_path: Mapped[str] = mapped_column(String(500))
    signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lease: Mapped["Lease"] = relationship(back_populates="documents")
