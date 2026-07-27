import uuid
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.payments import PaymentSchedule, RentPayment, Deposit
from app.models.leases import Lease
from app.schemas.payment import PaymentScheduleCreate, PaymentScheduleUpdate, PaymentScheduleResponse, RentPaymentCreate, RentPaymentResponse, DepositCreate, DepositUpdate, DepositResponse
from app.api.deps import get_current_manager
from app.services.receipt_service import generate_receipt_pdf

router = APIRouter()


# Payment Schedules
@router.get("/schedules/", response_model=List[PaymentScheduleResponse])
def list_schedules(
    lease_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    overdue: bool = Query(False),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(PaymentSchedule)
    if lease_id:
        query = query.filter(PaymentSchedule.lease_id == lease_id)
    if status:
        query = query.filter(PaymentSchedule.status == status)
    if overdue:
        query = query.filter(PaymentSchedule.due_date < date.today(), PaymentSchedule.status != "PAID")
    return query.order_by(PaymentSchedule.due_date).all()


@router.post("/schedules/", response_model=PaymentScheduleResponse)
def create_schedule(
    data: PaymentScheduleCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    schedule = PaymentSchedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.put("/schedules/{schedule_id}", response_model=PaymentScheduleResponse)
def update_schedule(
    schedule_id: uuid.UUID,
    data: PaymentScheduleUpdate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    schedule = db.query(PaymentSchedule).filter(PaymentSchedule.schedule_id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    db.commit()
    db.refresh(schedule)
    return schedule


# Rent Payments
@router.get("/", response_model=List[RentPaymentResponse])
def list_payments(
    lease_id: Optional[uuid.UUID] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(RentPayment)
    if lease_id:
        query = query.filter(RentPayment.lease_id == lease_id)
    if from_date:
        query = query.filter(RentPayment.payment_date >= from_date)
    if to_date:
        query = query.filter(RentPayment.payment_date <= to_date)
    return query.order_by(RentPayment.payment_date.desc()).all()


@router.post("/", response_model=RentPaymentResponse)
def record_payment(
    data: RentPaymentCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    payment = RentPayment(**data.model_dump())
    db.add(payment)
    db.flush()

    # Auto-update schedule status if linked
    if data.schedule_id:
        schedule = db.query(PaymentSchedule).filter(PaymentSchedule.schedule_id == data.schedule_id).first()
        if schedule:
            total_paid = db.query(func.sum(RentPayment.amount_paid)).filter(
                RentPayment.schedule_id == data.schedule_id
            ).scalar() or 0
            if total_paid >= schedule.amount_due:
                schedule.status = "PAID"

    db.commit()
    db.refresh(payment)

    # Generate receipt PDF
    try:
        receipt_path = generate_receipt_pdf(db, payment)
    except Exception:
        receipt_path = None

    return payment


@router.get("/{payment_id}/receipt")
def download_receipt(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    payment = db.query(RentPayment).filter(RentPayment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    from fastapi.responses import FileResponse
    import os
    receipt_path = f"app/static/receipts/{payment.receipt_number}.pdf"
    if not os.path.exists(receipt_path):
        receipt_path = generate_receipt_pdf(db, payment)
    return FileResponse(receipt_path, filename=f"receipt_{payment.receipt_number}.pdf")


# Deposits
@router.get("/deposits/", response_model=List[DepositResponse])
def list_deposits(
    lease_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    query = db.query(Deposit)
    if lease_id:
        query = query.filter(Deposit.lease_id == lease_id)
    if status:
        query = query.filter(Deposit.status == status)
    return query.all()


@router.post("/deposits/", response_model=DepositResponse)
def create_deposit(
    data: DepositCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    deposit = Deposit(**data.model_dump())
    db.add(deposit)
    db.commit()
    db.refresh(deposit)
    return deposit


@router.put("/deposits/{deposit_id}", response_model=DepositResponse)
def update_deposit(
    deposit_id: uuid.UUID,
    data: DepositUpdate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    deposit = db.query(Deposit).filter(Deposit.deposit_id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(deposit, field, value)
    db.commit()
    db.refresh(deposit)
    return deposit
