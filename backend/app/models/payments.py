import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Date, DateTime, Numeric, Integer, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"

    schedule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.lease_id"))
    due_date: Mapped[date] = mapped_column(Date)
    amount_due: Mapped[float] = mapped_column(Numeric(18, 2))
    currency_code: Mapped[str] = mapped_column(String(3), default="USD")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, PAID, OVERDUE
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lease: Mapped["Lease"] = relationship(back_populates="payment_schedules")
    payments: Mapped[list["RentPayment"]] = relationship(back_populates="schedule")


class RentPayment(Base):
    __tablename__ = "rent_payments"

    payment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.lease_id"))
    schedule_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("payment_schedules.schedule_id"), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(50))  # CASH, BANK_TRANSFER, ECOCASH, ZIPIT, ONEMONEY, INNBUCKS
    currency_code: Mapped[str] = mapped_column(String(3))
    amount_paid: Mapped[float] = mapped_column(Numeric(18, 2))
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True)
    period_from: Mapped[date] = mapped_column(Date)
    period_to: Mapped[date] = mapped_column(Date)
    received_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_managers.manager_id"), nullable=True)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lease: Mapped["Lease"] = relationship(back_populates="rent_payments")
    schedule: Mapped[Optional["PaymentSchedule"]] = relationship(back_populates="payments")


class Deposit(Base):
    __tablename__ = "deposits"

    deposit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lease_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leases.lease_id"))
    amount: Mapped[float] = mapped_column(Numeric(18, 2))
    currency_code: Mapped[str] = mapped_column(String(3))
    held_by: Mapped[str] = mapped_column(String(20))  # LANDLORD, AGENT
    status: Mapped[str] = mapped_column(String(20), default="HELD")  # HELD, RETURNED, FORFEITED
    deductions_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True)
    deductions_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    returned_amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lease: Mapped["Lease"] = relationship(back_populates="deposits")
