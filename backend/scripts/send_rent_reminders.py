#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.leases import Lease, PaymentSchedule
from app.models.stakeholders import Tenant
from app.services.sms_service import send_sms
from app.utils.currency import format_currency


def main():
    db: Session = SessionLocal()
    today = date.today()

    # Upcoming reminders (3 days before)
    upcoming = db.query(PaymentSchedule).filter(
        PaymentSchedule.due_date == today + timedelta(days=3),
        PaymentSchedule.status == "PENDING",
    ).all()

    for sched in upcoming:
        lease = sched.lease
        if not lease or lease.status != "ACTIVE":
            continue
        tenant = lease.primary_tenant
        if not tenant:
            continue

        message = (
            f"Dear {tenant.full_name}, your rent of "
            f"{format_currency(sched.amount_due, sched.currency_code)} "
            f"is due on {sched.due_date.strftime('%d %b %Y')}. "
            f"Please pay via EcoCash/Zipit. -ZimRental"
        )
        ok = send_sms(tenant.phone, message)
        print(f"Reminder to {tenant.phone}: {'SENT' if ok else 'FAILED'}")

    # Overdue notices
    overdue = db.query(PaymentSchedule).filter(
        PaymentSchedule.due_date < today,
        PaymentSchedule.status == "PENDING",
    ).all()

    for sched in overdue:
        lease = sched.lease
        if not lease or lease.status != "ACTIVE":
            continue
        tenant = lease.primary_tenant
        if not tenant:
            continue

        message = (
            f"Dear {tenant.full_name}, your rent of "
            f"{format_currency(sched.amount_due, sched.currency_code)} "
            f"for {sched.due_date.strftime('%b %Y')} is OVERDUE. "
            f"Please settle immediately. -ZimRental"
        )
        ok = send_sms(tenant.phone, message)
        print(f"OVERDUE notice to {tenant.phone}: {'SENT' if ok else 'FAILED'}")

    db.close()


if __name__ == "__main__":
    main()
