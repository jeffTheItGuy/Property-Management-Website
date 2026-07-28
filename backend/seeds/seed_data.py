#!/usr/bin/env python3
import os
import sys
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.core.security import get_password_hash
from app.models.stakeholders import Landlord, PropertyManager, Tenant, TenantGuarantor
from app.models.properties import Property, Unit
from app.models.leases import Lease
from app.models.payments import PaymentSchedule, RentPayment, Deposit
from app.models.maintenance import MaintenanceCategory, MaintenanceRequest
from app.models.expenses import ExpenseCategory, Expense
from app.models.communications import SmsLog
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

db = SessionLocal()

# ─── Helpers ──────────────────────────────────────────────────────────

def get_or_create(model, filters, defaults=None):
    defaults = defaults or {}
    obj = db.query(model).filter_by(**filters).first()
    if obj:
        return obj, False
    obj = model(**{**filters, **defaults})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj, True

def rand_id():
    return uuid.uuid4()

# ─── Property Manager (so you can log in immediately) ─────────────────

manager, _ = get_or_create(
    PropertyManager,
    {"phone": "0772123456"},
    {
        "manager_id": rand_id(),
        "full_name": "Admin User",
        "national_id": "63-1234567A89",
        "email": "admin@zimrental.com",
        "password_hash": get_password_hash("password123"),
        "is_active": True,
    },
)
print(f"Manager: {manager.full_name} ({manager.phone})")

# ─── Landlords ────────────────────────────────────────────────────────

landlords_data = [
    {"full_name": "Tendai Moyo", "national_id": "63-1111111A11", "phone": "0773111111", "email": "tendai@email.co.zw", "address": "15 Samora Machel Ave, Harare", "bank_details": "CBZ 1234567890"},
    {"full_name": "Chipo Ndlovu", "national_id": "45-2222222B22", "phone": "0773222222", "email": "chipo@email.co.zw", "address": "22 Josiah Tongogara St, Bulawayo", "bank_details": "ZB Bank 0987654321"},
    {"full_name": "John Banda", "national_id": "63-3333333C33", "phone": "0773333333", "email": "john.banda@gmail.com", "address": "5 Robert Mugabe Way, Mutare", "bank_details": "Stanbic 1122334455"},
]

landlords = []
for d in landlords_data:
    ll, _ = get_or_create(Landlord, {"phone": d["phone"]}, {**d, "landlord_id": rand_id()})
    landlords.append(ll)
    print(f"Landlord: {ll.full_name}")

# ─── Tenants ──────────────────────────────────────────────────────────

tenants_data = [
    {"full_name": "Blessing Chikwava", "national_id": "78-4444444D44", "phone": "0774444444", "email": "blessing@email.co.zw", "employer_name": "Econet Wireless", "monthly_income": 850.00},
    {"full_name": "Sarah Marufu", "national_id": "78-5555555E55", "phone": "0775555555", "email": "sarah@email.co.zw", "employer_name": "NetOne", "monthly_income": 620.00},
    {"full_name": "Peter Dziva", "national_id": "78-6666666F66", "phone": "0776666666", "email": "peter@email.co.zw", "employer_name": "CABS Bank", "monthly_income": 1200.00},
    {"full_name": "Rudo Gumbo", "national_id": "78-7777777G77", "phone": "0777777777", "email": "rudo@email.co.zw", "employer_name": "TelOne", "monthly_income": 700.00},
    {"full_name": "Tafara Mupfumi", "national_id": "78-8888888H88", "phone": "0778888888", "email": "tafara@email.co.zw", "employer_name": "Self employed", "monthly_income": 950.00},
]

tenants = []
for d in tenants_data:
    t, _ = get_or_create(Tenant, {"phone": d["phone"]}, {**d, "tenant_id": rand_id()})
    tenants.append(t)
    print(f"Tenant: {t.full_name}")

# ─── Properties (with PostGIS geom) ───────────────────────────────────

properties_data = [
    {"property_code": "HRE001", "property_name": "Avondale Heights", "property_type": "APARTMENT", "address": "47 King George Rd, Avondale", "city": "Harare", "suburb": "Avondale", "latitude": -17.8019, "longitude": 31.0447, "landlord_idx": 0},
    {"property_code": "HRE002", "property_name": "Belvedere Family Home", "property_type": "HOUSE", "address": "12 Bath Rd, Belvedere", "city": "Harare", "suburb": "Belvedere", "latitude": -17.8201, "longitude": 31.0012, "landlord_idx": 0},
    {"property_code": "BYO001", "property_name": "Suburbs Cottage", "property_type": "COTTAGE", "address": "8 Lobengula St, Suburbs", "city": "Bulawayo", "suburb": "Suburbs", "latitude": -20.1325, "longitude": 28.6265, "landlord_idx": 1},
    {"property_code": "MUT001", "property_name": "Murambi Flats", "property_type": "APARTMENT", "address": "3 Herbert Chitepo St, Murambi", "city": "Mutare", "suburb": "Murambi", "latitude": -18.9707, "longitude": 32.6709, "landlord_idx": 2},
    {"property_code": "HRE003", "property_name": "Avenues Office Block", "property_type": "OFFICE", "address": "101 Sam Nujoma St, Avenues", "city": "Harare", "suburb": "Avenues", "latitude": -17.8252, "longitude": 31.0335, "landlord_idx": 1},
]

properties = []
for d in properties_data:
    existing = db.query(Property).filter(Property.property_code == d["property_code"]).first()
    if existing:
        properties.append(existing)
        continue

    geom = from_shape(Point(d["longitude"], d["latitude"]), srid=4326)
    prop = Property(
        property_id=rand_id(),
        landlord_id=landlords[d["landlord_idx"]].landlord_id,
        manager_id=manager.manager_id,
        property_code=d["property_code"],
        property_name=d["property_name"],
        property_type=d["property_type"],
        address=d["address"],
        city=d["city"],
        suburb=d["suburb"],
        status="ACTIVE",
        geom=geom,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    properties.append(prop)
    print(f"Property: {prop.property_name} ({prop.city})")

# ─── Units ────────────────────────────────────────────────────────────

units_data = [
    # HRE001 - Avondale Heights (Apartment)
    {"property_idx": 0, "unit_number": "A1", "unit_type": "2_BED", "rent": 450.00, "deposit": 2},
    {"property_idx": 0, "unit_number": "A2", "unit_type": "1_BED", "rent": 320.00, "deposit": 2},
    {"property_idx": 0, "unit_number": "B1", "unit_type": "3_BED", "rent": 600.00, "deposit": 2},
    # HRE002 - Belvedere House
    {"property_idx": 1, "unit_number": "Main", "unit_type": "4_BED", "rent": 800.00, "deposit": 2},
    {"property_idx": 1, "unit_number": "Cottage", "unit_type": "1_BED", "rent": 280.00, "deposit": 1},
    # BYO001 - Suburbs Cottage
    {"property_idx": 2, "unit_number": "Main", "unit_type": "2_BED", "rent": 350.00, "deposit": 2},
    # MUT001 - Murambi Flats
    {"property_idx": 3, "unit_number": "1A", "unit_type": "2_BED", "rent": 300.00, "deposit": 2},
    {"property_idx": 3, "unit_number": "1B", "unit_type": "1_BED", "rent": 220.00, "deposit": 2},
    # HRE003 - Office Block
    {"property_idx": 4, "unit_number": "Suite 101", "unit_type": "OFFICE", "rent": 550.00, "deposit": 3},
]

units = []
for d in units_data:
    existing = db.query(Unit).filter(
        Unit.property_id == properties[d["property_idx"]].property_id,
        Unit.unit_number == d["unit_number"]
    ).first()
    if existing:
        units.append(existing)
        continue

    unit = Unit(
        unit_id=rand_id(),
        property_id=properties[d["property_idx"]].property_id,
        unit_number=d["unit_number"],
        unit_type=d["unit_type"],
        current_rent=d["rent"],
        rent_currency="USD",
        deposit_months=d["deposit"],
        status="VACANT",
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    units.append(unit)
    print(f"Unit: {unit.unit_number} @ {unit.property.property_name}")

# ─── Leases ───────────────────────────────────────────────────────────

leases_data = [
    {"unit_idx": 0, "tenant_idx": 0, "lease_number": "L-2026-001", "rent": 450.00, "deposit": 900.00, "start": date(2026, 1, 1), "end": date(2026, 12, 31), "due_day": 5},
    {"unit_idx": 1, "tenant_idx": 1, "lease_number": "L-2026-002", "rent": 320.00, "deposit": 640.00, "start": date(2026, 2, 1), "end": date(2027, 1, 31), "due_day": 1},
    {"unit_idx": 3, "tenant_idx": 2, "lease_number": "L-2026-003", "rent": 800.00, "deposit": 1600.00, "start": date(2026, 1, 1), "end": date(2026, 12, 31), "due_day": 1},
    {"unit_idx": 5, "tenant_idx": 3, "lease_number": "L-2026-004", "rent": 350.00, "deposit": 700.00, "start": date(2026, 3, 1), "end": date(2027, 2, 28), "due_day": 3},
    {"unit_idx": 6, "tenant_idx": 4, "lease_number": "L-2026-005", "rent": 300.00, "deposit": 600.00, "start": date(2026, 1, 1), "end": date(2026, 6, 30), "due_day": 1},
]

leases = []
for d in leases_data:
    existing = db.query(Lease).filter(Lease.lease_number == d["lease_number"]).first()
    if existing:
        leases.append(existing)
        continue

    lease = Lease(
        lease_id=rand_id(),
        lease_number=d["lease_number"],
        unit_id=units[d["unit_idx"]].unit_id,
        primary_tenant_id=tenants[d["tenant_idx"]].tenant_id,
        start_date=d["start"],
        end_date=d["end"],
        base_rent=d["rent"],
        rent_currency="USD",
        deposit_amount=d["deposit"],
        payment_due_day=d["due_day"],
        status="ACTIVE",
    )
    db.add(lease)
    # mark unit occupied
    units[d["unit_idx"]].status = "OCCUPIED"
    db.commit()
    db.refresh(lease)
    leases.append(lease)
    print(f"Lease: {lease.lease_number} ({lease.base_rent} USD)")

# ─── Payment Schedules ────────────────────────────────────────────────

schedules = []
today = date.today()
for lease in leases:
    # Generate 6 months of schedules
    for i in range(6):
        due = date(today.year, today.month, lease.payment_due_day) + timedelta(days=30*i)
        if due.day != lease.payment_due_day:
            due = due.replace(day=lease.payment_due_day)

        sched_id = rand_id()
        status = "PAID" if i < 2 else ("OVERDUE" if i == 2 and due < today else "PENDING")
        sched = PaymentSchedule(
            schedule_id=sched_id,
            lease_id=lease.lease_id,
            due_date=due,
            amount_due=lease.base_rent,
            currency_code="USD",
            status=status,
        )
        db.add(sched)
        db.commit()
        db.refresh(sched)
        schedules.append(sched)

        # Record payment for paid schedules
        if status == "PAID":
            payment = RentPayment(
                payment_id=rand_id(),
                lease_id=lease.lease_id,
                schedule_id=sched.schedule_id,
                payment_method="ECOCASH" if i % 2 == 0 else "BANK_TRANSFER",
                currency_code="USD",
                amount_paid=lease.base_rent,
                receipt_number=f"RCP-{lease.lease_number}-{i+1}",
                period_from=due.replace(day=1),
                period_to=(due + timedelta(days=32)).replace(day=1) - timedelta(days=1),
                received_by=manager.manager_id,
            )
            db.add(payment)
            db.commit()
            print(f"  Payment: {payment.receipt_number} {payment.amount_paid} USD")

    print(f"Schedules created for {lease.lease_number}")

# ─── Deposits ─────────────────────────────────────────────────────────

for lease in leases:
    existing = db.query(Deposit).filter(Deposit.lease_id == lease.lease_id).first()
    if not existing:
        dep = Deposit(
            deposit_id=rand_id(),
            lease_id=lease.lease_id,
            amount=lease.deposit_amount,
            currency_code="USD",
            held_by="LANDLORD",
            status="HELD",
        )
        db.add(dep)
        db.commit()
        print(f"Deposit: {dep.amount} USD held for {lease.lease_number}")

# ─── Maintenance Categories ───────────────────────────────────────────

maint_cats = [
    "Plumbing", "Electrical", "Carpentry", "Painting", "Roofing", "Security", "Appliance", "General Cleaning", "Other"
]
for name in maint_cats:
    cat, _ = get_or_create(MaintenanceCategory, {"category_name": name}, {"category_id": rand_id()})

# ─── Maintenance Requests ─────────────────────────────────────────────

maint_requests = [
    {"unit_idx": 0, "title": "Leaking kitchen tap", "priority": "MEDIUM", "status": "COMPLETED"},
    {"unit_idx": 1, "title": "Geyser not heating", "priority": "HIGH", "status": "IN_PROGRESS"},
    {"unit_idx": 3, "title": "Broken boundary wall gate", "priority": "MEDIUM", "status": "OPEN"},
    {"unit_idx": 6, "title": "Blocked toilet", "priority": "EMERGENCY", "status": "OPEN"},
]

for d in maint_requests:
    req = MaintenanceRequest(
        request_id=rand_id(),
        unit_id=units[d["unit_idx"]].unit_id,
        title=d["title"],
        priority=d["priority"],
        status=d["status"],
    )
    db.add(req)
    db.commit()
    print(f"Maintenance: {d['title']} ({d['status']})")

# ─── Expense Categories ───────────────────────────────────────────────

exp_cats = [
    {"name": "Council Rates", "deductible": True},
    {"name": "ZESA", "deductible": True},
    {"name": "Water", "deductible": True},
    {"name": "Insurance", "deductible": True},
    {"name": "Maintenance", "deductible": True},
    {"name": "Security", "deductible": True},
    {"name": "Gardening", "deductible": True},
    {"name": "Other", "deductible": False},
]
for c in exp_cats:
    get_or_create(ExpenseCategory, {"category_name": c["name"]}, {
        "category_id": rand_id(),
        "description": f"Expense for {c['name']}",
    })

# ─── Expenses ─────────────────────────────────────────────────────────

expenses_data = [
    {"property_idx": 0, "type": "ZESA", "amount": 180.00, "supplier": "ZESA Holdings", "date": date(2026, 7, 1)},
    {"property_idx": 0, "type": "Water", "amount": 45.00, "supplier": "City of Harare", "date": date(2026, 7, 5)},
    {"property_idx": 1, "type": "Council Rates", "amount": 120.00, "supplier": "City of Harare", "date": date(2026, 7, 1)},
    {"property_idx": 2, "type": "Maintenance", "amount": 85.00, "supplier": "BuildAll Hardware", "date": date(2026, 7, 10)},
    {"property_idx": 3, "type": "Security", "amount": 150.00, "supplier": "Safeguard Security", "date": date(2026, 7, 1)},
]

for d in expenses_data:
    exp = Expense(
        expense_id=rand_id(),
        property_id=properties[d["property_idx"]].property_id,
        expense_type=d["type"],
        amount=d["amount"],
        currency_code="USD",
        supplier_name=d["supplier"],
        invoice_date=d["date"],
    )
    db.add(exp)
    db.commit()
    print(f"Expense: {d['type']} {d['amount']} USD")

# ─── SMS Logs ─────────────────────────────────────────────────────────

sms = SmsLog(
    sms_id=rand_id(),
    recipient_type="TENANT",
    phone="0774444444",
    message="Dear Blessing, your rent of USD 450.00 is due on 05 Jul 2026. Please pay via EcoCash/Zipit. -ZimRental",
    status="SENT",
    sent_at=datetime.now(),
)
db.add(sms)
db.commit()

print("\n✅ Seed complete. You can now log in with:")
print("   Phone: 0772123456")
print("   Password: password123")