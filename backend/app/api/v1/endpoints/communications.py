import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.communications import SmsLog
from app.models.stakeholders import Tenant, Landlord
from app.models.leases import Lease
from app.schemas.communication import SmsLogCreate, SmsLogResponse
from app.api.deps import get_current_manager
from app.services.sms_service import send_sms

router = APIRouter()


@router.get("/sms/", response_model=List[SmsLogResponse])
def list_sms_logs(
    phone: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(SmsLog)
    if phone:
        query = query.filter(SmsLog.phone == phone)
    if status:
        query = query.filter(SmsLog.status == status)
    return query.order_by(SmsLog.created_at.desc()).all()


@router.post("/sms/send")
def send_manual_sms(
    data: SmsLogCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    """Send an SMS and log it."""
    result = send_sms(phone=data.phone, message=data.message)
    log = SmsLog(
        recipient_type=data.recipient_type,
        recipient_id=data.recipient_id,
        phone=data.phone,
        message=data.message,
        status="SENT" if result else "FAILED",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.post("/sms/lease-reminder/{lease_id}")
def send_lease_reminder(
    lease_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    """Send rent due reminder to primary tenant of a lease."""
    lease = db.query(Lease).filter(Lease.lease_id == lease_id).first()
    if not lease or not lease.primary_tenant:
        raise HTTPException(status_code=404, detail="Lease or tenant not found")

    tenant = lease.primary_tenant
    message = f"Dear {tenant.full_name}, your rent of {lease.base_rent} {lease.rent_currency} is due on {lease.payment_due_day}st of this month. Please pay via EcoCash/Zipit. -ZimRental"

    result = send_sms(phone=tenant.phone, message=message)
    log = SmsLog(
        recipient_type="TENANT",
        recipient_id=tenant.tenant_id,
        phone=tenant.phone,
        message=message,
        status="SENT" if result else "FAILED",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
