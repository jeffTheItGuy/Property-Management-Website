import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point

from app.database import get_db
from app.models.properties import Property, PropertyDocument, Unit
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyDocumentResponse, UnitCreate, UnitUpdate, UnitResponse
from app.api.deps import get_current_manager
from app.services.geospatial_service import search_properties_nearby, properties_to_geojson

router = APIRouter()


@router.get("/", response_model=List[PropertyResponse])
def list_properties(
    city: Optional[str] = Query(None),
    suburb: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(Property)
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if suburb:
        query = query.filter(Property.suburb.ilike(f"%{suburb}%"))
    if status:
        query = query.filter(Property.status == status)
    if search:
        query = query.filter(Property.property_name.ilike(f"%{search}%"))
    return query.order_by(Property.created_at.desc()).all()


@router.post("/", response_model=PropertyResponse)
def create_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    existing = db.query(Property).filter(Property.property_code == data.property_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Property code already exists")

    geom = None
    if data.latitude is not None and data.longitude is not None:
        geom = from_shape(Point(data.longitude, data.latitude), srid=4326)

    prop_data = data.model_dump(exclude={"latitude", "longitude"})
    prop = Property(**prop_data, geom=geom)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: uuid.UUID,
    data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    update_data = data.model_dump(exclude_unset=True)
    if "latitude" in update_data and "longitude" in update_data:
        lat = update_data.pop("latitude")
        lon = update_data.pop("longitude")
        if lat is not None and lon is not None:
            prop.geom = from_shape(Point(lon, lat), srid=4326)

    for field, value in update_data.items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{property_id}")
def delete_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(prop)
    db.commit()
    return {"detail": "Property deleted"}


# Geospatial endpoints
@router.get("/geo/nearby")
def nearby_properties(
    lat: float,
    lon: float,
    radius_km: float = Query(5.0, ge=0.1, le=50),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    """Find properties within radius_km of a point."""
    properties = search_properties_nearby(db, lon, lat, radius_km)
    return properties_to_geojson(properties)


@router.get("/geo/all")
def all_properties_geojson(
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    """Export all properties as GeoJSON."""
    properties = db.query(Property).filter(Property.geom.isnot(None)).all()
    return properties_to_geojson(properties)


# Documents
@router.post("/{property_id}/documents")
def upload_property_document(
    property_id: uuid.UUID,
    document_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    import os, shutil
    upload_dir = "app/static/uploads/properties"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{property_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = PropertyDocument(property_id=property_id, document_type=document_type, file_path=file_path)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return PropertyDocumentResponse.model_validate(doc)


# Units nested under property
@router.get("/{property_id}/units", response_model=List[UnitResponse])
def list_property_units(
    property_id: uuid.UUID,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(Unit).filter(Unit.property_id == property_id)
    if status:
        query = query.filter(Unit.status == status)
    return query.order_by(Unit.unit_number).all()


@router.post("/{property_id}/units", response_model=UnitResponse)
def create_unit(
    property_id: uuid.UUID,
    data: UnitCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    data.property_id = property_id
    unit = Unit(**data.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit
