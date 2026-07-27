import uuid
from datetime import datetime
from typing import List, Optional, Any

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.database import Base
from app.models.inspections import Inspection


class Property(Base):
    __tablename__ = "properties"

    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    landlord_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("landlords.landlord_id"))
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("property_managers.manager_id"), nullable=True)
    property_code: Mapped[str] = mapped_column(String(20), unique=True)
    property_name: Mapped[str] = mapped_column(String(200))
    property_type: Mapped[str] = mapped_column(String(50))  # HOUSE, COTTAGE, APARTMENT, OFFICE, SHOP, INDUSTRIAL
    address: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100))
    suburb: Mapped[str] = mapped_column(String(100))
    council_zone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    stand_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    deed_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amenities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE
    geom: Mapped[Optional[Any]] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    landlord: Mapped["Landlord"] = relationship(back_populates="properties")
    manager: Mapped[Optional["PropertyManager"]] = relationship(back_populates="properties")
    units: Mapped[List["Unit"]] = relationship(back_populates="property")
    documents: Mapped[List["PropertyDocument"]] = relationship(back_populates="property")
    expenses: Mapped[List["Expense"]] = relationship(back_populates="property")


class PropertyDocument(Base):
    __tablename__ = "property_documents"

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.property_id"))
    document_type: Mapped[str] = mapped_column(String(50))  # TITLE_DEED, COUNCIL_CERT, INSURANCE, PHOTO
    file_path: Mapped[str] = mapped_column(String(500))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    property: Mapped["Property"] = relationship(back_populates="documents")


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = ()

    unit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.property_id"))
    unit_number: Mapped[str] = mapped_column(String(20))
    unit_type: Mapped[str] = mapped_column(String(50))  # BEDSITTER, 1_BED, 2_BED, 3_BED, 4_BED, OFFICE, SHOP, WAREHOUSE
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_rent: Mapped[float] = mapped_column(Numeric(18, 2))
    rent_currency: Mapped[str] = mapped_column(String(3), default="USD")
    deposit_months: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="VACANT")  # VACANT, OCCUPIED, MAINTENANCE
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    property: Mapped["Property"] = relationship(back_populates="units")
    leases: Mapped[List["Lease"]] = relationship(back_populates="unit")
    maintenance_requests: Mapped[List["MaintenanceRequest"]] = relationship(back_populates="unit")
    inspections: Mapped[List["Inspection"]] = relationship(back_populates="unit")
    expenses: Mapped[List["Expense"]] = relationship(back_populates="unit")