import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.leases import Lease, LeaseTenant, LeaseDocument
from app.models.properties import Unit
from app.schemas.lease import LeaseCreate, LeaseUpdate, LeaseResponse, LeaseTenantCreate, LeaseTenantResponse, LeaseDocumentCreate, LeaseDocumentResponse
from app.api.deps import get_current_manager

router = APIRouter()


@router.get("/", response_model=List[LeaseResponse])
def list_leases(
    unit_id: Optional[uuid.UUID] = Query(None),
    tenant_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(Lease)
    if unit_id:
        query = query.filter(Lease.unit_id == unit_id)
    if tenant_id:
        query = query.filter(Lease.primary_tenant_id == tenant_id)
    if status:
        query = query.filter(Lease.status == status)
    return query.order_by(Lease.start_date.desc()).all()


@router.post("/", response_model=LeaseResponse)
def create_lease(
    data: LeaseCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    existing = db.query(Lease).filter(Lease.lease_number == data.lease_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Lease number already exists")

    # Update unit status to OCCUPIED if lease is ACTIVE
    lease = Lease(**data.model_dump())
    db.add(lease)
    db.flush()

    if data.status == "ACTIVE":
        unit = db.query(Unit).filter(Unit.unit_id == data.unit_id).first()
        if unit:
            unit.status = "OCCUPIED"

    db.commit()
    db.refresh(lease)
    return lease


@router.get("/{lease_id}", response_model=LeaseResponse)
def get_lease(
    lease_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    lease = db.query(Lease).filter(Lease.lease_id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    return lease


@router.put("/{lease_id}", response_model=LeaseResponse)
def update_lease(
    lease_id: uuid.UUID,
    data: LeaseUpdate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    lease = db.query(Lease).filter(Lease.lease_id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")

    old_status = lease.status
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lease, field, value)

    # Update unit status on lease status change
    if data.status and data.status != old_status:
        unit = db.query(Unit).filter(Unit.unit_id == lease.unit_id).first()
        if unit:
            if data.status == "ACTIVE":
                unit.status = "OCCUPIED"
            elif data.status in ("ENDED", "BREACHED"):
                unit.status = "VACANT"

    db.commit()
    db.refresh(lease)
    return lease


@router.delete("/{lease_id}")
def delete_lease(
    lease_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    lease = db.query(Lease).filter(Lease.lease_id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    db.delete(lease)
    db.commit()
    return {"detail": "Lease deleted"}


# Lease tenants
@router.post("/{lease_id}/tenants", response_model=LeaseTenantResponse)
def add_lease_tenant(
    lease_id: uuid.UUID,
    data: LeaseTenantCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    data.lease_id = lease_id
    lt = LeaseTenant(**data.model_dump())
    db.add(lt)
    db.commit()
    db.refresh(lt)
    return lt


# Lease documents
@router.post("/{lease_id}/documents", response_model=LeaseDocumentResponse)
def add_lease_document(
    lease_id: uuid.UUID,
    data: LeaseDocumentCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    data.lease_id = lease_id
    doc = LeaseDocument(**data.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
