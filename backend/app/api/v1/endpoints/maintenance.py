import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
import os, shutil

from app.database import get_db
from app.models.maintenance import MaintenanceCategory, MaintenanceRequest, MaintenancePhoto
from app.schemas.maintenance import MaintenanceCategoryCreate, MaintenanceCategoryResponse, MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceRequestResponse, MaintenancePhotoResponse
from app.api.deps import get_current_manager

router = APIRouter()


# Categories
@router.get("/categories/", response_model=List[MaintenanceCategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    return db.query(MaintenanceCategory).filter(MaintenanceCategory.is_active == True).all()


@router.post("/categories/", response_model=MaintenanceCategoryResponse)
def create_category(
    data: MaintenanceCategoryCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    cat = MaintenanceCategory(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# Requests
@router.get("/requests/", response_model=List[MaintenanceRequestResponse])
def list_requests(
    unit_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(MaintenanceRequest)
    if unit_id:
        query = query.filter(MaintenanceRequest.unit_id == unit_id)
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    if priority:
        query = query.filter(MaintenanceRequest.priority == priority)
    return query.order_by(MaintenanceRequest.reported_at.desc()).all()


@router.post("/requests/", response_model=MaintenanceRequestResponse)
def create_request(
    data: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    req = MaintenanceRequest(**data.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/requests/{request_id}", response_model=MaintenanceRequestResponse)
def get_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


@router.put("/requests/{request_id}", response_model=MaintenanceRequestResponse)
def update_request(
    request_id: uuid.UUID,
    data: MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    req = db.query(MaintenanceRequest).filter(MaintenanceRequest.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(req, field, value)
    db.commit()
    db.refresh(req)
    return req


@router.post("/requests/{request_id}/photos")
def upload_photo(
    request_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    upload_dir = "app/static/uploads/maintenance"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{request_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    photo = MaintenancePhoto(request_id=request_id, file_path=file_path)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return MaintenancePhotoResponse.model_validate(photo)
