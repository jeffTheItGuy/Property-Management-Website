import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from sqlalchemy.orm import Session

from app.models.payments import RentPayment
from app.models.leases import Lease
from app.models.stakeholders import Tenant


def generate_receipt_pdf(db: Session, payment: RentPayment) -> str:
    """Generate a ZIMRA-friendly PDF receipt."""
    lease = db.query(Lease).filter(Lease.lease_id == payment.lease_id).first()
    tenant = None
    if lease:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == lease.primary_tenant_id).first()

    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("receipt_base.html")

    html_out = template.render(
        receipt_number=payment.receipt_number,
        payment_date=payment.payment_date.strftime("%d %b %Y") if payment.payment_date else "",
        tenant_name=tenant.full_name if tenant else "",
        tenant_phone=tenant.phone if tenant else "",
        amount_paid=payment.amount_paid,
        currency=payment.currency_code,
        payment_method=payment.payment_method,
        reference_number=payment.reference_number or "",
        period_from=payment.period_from.strftime("%d %b %Y"),
        period_to=payment.period_to.strftime("%d %b %Y"),
        notes=payment.notes or "",
        generated_at=datetime.now().strftime("%d %b %Y %H:%M"),
    )

    output_dir = "app/static/receipts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{payment.receipt_number}.pdf"
    HTML(string=html_out).write_pdf(output_path)
    return output_path
