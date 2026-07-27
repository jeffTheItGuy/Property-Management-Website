import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.properties import Unit
from app.schemas.property import UnitUpdate, UnitResponse
from app.api.deps import get_current_manager

router = APIRouter()


@router.get("/", response_model=List[UnitResponse])
def list_units(
    property_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    unit_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(Unit)
    if property_id:
        query = query.filter(Unit.property_id == property_id)
    if status:
        query = query.filter(Unit.status == status)
    if unit_type:
        query = query.filter(Unit.unit_type == unit_type)
    return query.order_by(Unit.created_at.desc()).all()


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: uuid.UUID,
    data: UnitUpdate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/{unit_id}")
def delete_unit(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()
    return {"detail": "Unit deleted"}
