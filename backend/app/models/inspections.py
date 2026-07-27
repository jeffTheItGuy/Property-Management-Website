import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Text, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.lease_id"), nullable=True)
    unit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("units.unit_id"))
    inspection_type: Mapped[str] = mapped_column(String(20))  # MOVE_IN, MOVE_OUT, PERIODIC
    scheduled_date: Mapped[date] = mapped_column(Date)
    conducted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    conducted_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tenant_present: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    overall_condition: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # GOOD, FAIR, POOR, DAMAGED
    condition_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    damages_noted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lease: Mapped[Optional["Lease"]] = relationship(back_populates="inspections")
    unit: Mapped["Unit"] = relationship(back_populates="inspections")
