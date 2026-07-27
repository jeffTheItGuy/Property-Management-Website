import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.stakeholders import Landlord
from app.schemas.stakeholder import LandlordCreate, LandlordUpdate, LandlordResponse
from app.api.deps import get_current_manager

router = APIRouter()


@router.get("/", response_model=List[LandlordResponse])
def list_landlords(
    search: Optional[str] = Query(None, description="Search name or phone"),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(Landlord)
    if search:
        query = query.filter(
            (Landlord.full_name.ilike(f"%{search}%")) | (Landlord.phone.ilike(f"%{search}%"))
        )
    if is_active is not None:
        query = query.filter(Landlord.is_active == is_active)
    return query.order_by(Landlord.created_at.desc()).all()


@router.post("/", response_model=LandlordResponse)
def create_landlord(
    data: LandlordCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    existing = db.query(Landlord).filter(Landlord.national_id == data.national_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Landlord with this national ID already exists")
    landlord = Landlord(**data.model_dump())
    db.add(landlord)
    db.commit()
    db.refresh(landlord)
    return landlord


@router.get("/{landlord_id}", response_model=LandlordResponse)
def get_landlord(
    landlord_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    landlord = db.query(Landlord).filter(Landlord.landlord_id == landlord_id).first()
    if not landlord:
        raise HTTPException(status_code=404, detail="Landlord not found")
    return landlord


@router.put("/{landlord_id}", response_model=LandlordResponse)
def update_landlord(
    landlord_id: uuid.UUID,
    data: LandlordUpdate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    landlord = db.query(Landlord).filter(Landlord.landlord_id == landlord_id).first()
    if not landlord:
        raise HTTPException(status_code=404, detail="Landlord not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(landlord, field, value)
    db.commit()
    db.refresh(landlord)
    return landlord


@router.delete("/{landlord_id}")
def delete_landlord(
    landlord_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    landlord = db.query(Landlord).filter(Landlord.landlord_id == landlord_id).first()
    if not landlord:
        raise HTTPException(status_code=404, detail="Landlord not found")
    db.delete(landlord)
    db.commit()
    return {"detail": "Landlord deleted"}
