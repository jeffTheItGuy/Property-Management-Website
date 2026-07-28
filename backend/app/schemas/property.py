import uuid
from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict, model_validator, field_serializer

from app.database import Base  # if needed elsewhere


class PropertyDocumentBase(BaseModel):
    property_id: uuid.UUID
    document_type: str
    file_path: str


class PropertyDocumentResponse(PropertyDocumentBase):
    document_id: uuid.UUID
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PropertyBase(BaseModel):
    landlord_id: uuid.UUID
    manager_id: Optional[uuid.UUID] = None
    property_code: str
    property_name: str
    property_type: str
    address: str
    city: str
    suburb: str
    council_zone: Optional[str] = None
    stand_number: Optional[str] = None
    deed_number: Optional[str] = None
    description: Optional[str] = None
    amenities: Optional[str] = None
    status: str = "ACTIVE"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    landlord_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    property_code: Optional[str] = None
    property_name: Optional[str] = None
    property_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    suburb: Optional[str] = None
    council_zone: Optional[str] = None
    stand_number: Optional[str] = None
    deed_number: Optional[str] = None
    description: Optional[str] = None
    amenities: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyResponse(PropertyBase):
    property_id: uuid.UUID
    geom: Optional[Any] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def extract_lat_lon_from_geom(cls, data):
        """Pull latitude/longitude out of the PostGIS geom column so the frontend map works."""
        if hasattr(data, 'geom') and data.geom is not None:
            try:
                from geoalchemy2.shape import to_shape
                shape = to_shape(data.geom)
                data.latitude = shape.y
                data.longitude = shape.x
            except Exception:
                pass
        return data

    @field_serializer('geom')
    def serialize_geom(self, geom):
        """Convert WKBElement to a GeoJSON-like dict so Pydantic doesn't choke."""
        if geom is None:
            return None
        try:
            from geoalchemy2.shape import to_shape
            from shapely.geometry import mapping
            return mapping(to_shape(geom))
        except Exception:
            return None


class UnitBase(BaseModel):
    property_id: uuid.UUID
    unit_number: str
    unit_type: str
    description: Optional[str] = None
    current_rent: float
    rent_currency: str = "USD"
    deposit_months: int = 1
    status: str = "VACANT"


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    unit_number: Optional[str] = None
    unit_type: Optional[str] = None
    description: Optional[str] = None
    current_rent: Optional[float] = None
    rent_currency: Optional[str] = None
    deposit_months: Optional[int] = None
    status: Optional[str] = None


class UnitResponse(UnitBase):
    unit_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)