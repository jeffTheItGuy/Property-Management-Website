import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, DateTime, Numeric, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MaintenanceCategory(Base):
    __tablename__ = "maintenance_categories"

    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    requests: Mapped[List["MaintenanceRequest"]] = relationship(back_populates="category")


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.lease_id"), nullable=True)
    unit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("units.unit_id"))
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("maintenance_categories.category_id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, EMERGENCY
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN, IN_PROGRESS, COMPLETED, CANCELLED
    assigned_to: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cost_estimate: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True)
    final_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True)
    currency_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lease: Mapped[Optional["Lease"]] = relationship(back_populates="maintenance_requests")
    unit: Mapped["Unit"] = relationship(back_populates="maintenance_requests")
    category: Mapped[Optional["MaintenanceCategory"]] = relationship(back_populates="requests")
    photos: Mapped[List["MaintenancePhoto"]] = relationship(back_populates="request")


class MaintenancePhoto(Base):
    __tablename__ = "maintenance_photos"

    photo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("maintenance_requests.request_id"))
    file_path: Mapped[str] = mapped_column(String(500))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped["MaintenanceRequest"] = relationship(back_populates="photos")