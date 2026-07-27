import os
import json
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geoalchemy2.shape import to_shape

from app.models.payments import RentPayment, PaymentSchedule
from app.models.expenses import Expense
from app.models.properties import Property
from app.models.leases import Lease


def generate_monthly_report_excel(db: Session, year: int, month: int, property_id: Optional[str] = None) -> str:
    """Generate Excel report with income, expenses, and occupancy."""

    # Income
    income_query = db.query(RentPayment).filter(
        extract("year", RentPayment.payment_date) == year,
        extract("month", RentPayment.payment_date) == month,
    )
    if property_id:
        income_query = income_query.join(Lease).filter(Lease.unit.has(property_id=property_id))
    income = income_query.all()

    income_data = [{
        "receipt_number": p.receipt_number,
        "date": p.payment_date,
        "amount": float(p.amount_paid),
        "currency": p.currency_code,
        "method": p.payment_method,
    } for p in income]
    df_income = pd.DataFrame(income_data)

    # Expenses
    expense_query = db.query(Expense).filter(
        extract("year", Expense.invoice_date) == year,
        extract("month", Expense.invoice_date) == month,
    )
    if property_id:
        expense_query = expense_query.filter(Expense.property_id == property_id)
    expenses = expense_query.all()

    expense_data = [{
        "type": e.expense_type,
        "supplier": e.supplier_name,
        "amount": float(e.amount),
        "currency": e.currency_code,
        "date": e.invoice_date,
    } for e in expenses]
    df_expense = pd.DataFrame(expense_data)

    # Write to Excel
    output_dir = "app/static/reports"
    os.makedirs(output_dir, exist_ok=True)
    file_path = f"{output_dir}/monthly_report_{year}_{month:02d}.xlsx"

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_income.to_excel(writer, sheet_name="Income", index=False)
        df_expense.to_excel(writer, sheet_name="Expenses", index=False)

        # Summary sheet
        summary = pd.DataFrame({
            "Metric": ["Total Income", "Total Expenses", "Net"],
            "Amount": [
                df_income["amount"].sum() if not df_income.empty else 0,
                df_expense["amount"].sum() if not df_expense.empty else 0,
                (df_income["amount"].sum() if not df_income.empty else 0) - (df_expense["amount"].sum() if not df_expense.empty else 0)
            ]
        })
        summary.to_excel(writer, sheet_name="Summary", index=False)

    return file_path


def generate_payment_ledger_excel(db: Session, from_date: date, to_date: date, lease_id: Optional[str] = None) -> str:
    """Export payment ledger as Excel."""
    query = db.query(RentPayment).filter(
        RentPayment.payment_date >= from_date,
        RentPayment.payment_date <= to_date,
    )
    if lease_id:
        query = query.filter(RentPayment.lease_id == lease_id)
    payments = query.order_by(RentPayment.payment_date).all()

    data = [{
        "receipt_number": p.receipt_number,
        "date": p.payment_date,
        "amount": float(p.amount_paid),
        "currency": p.currency_code,
        "method": p.payment_method,
        "reference": p.reference_number,
        "period": f"{p.period_from} to {p.period_to}",
    } for p in payments]

    df = pd.DataFrame(data)
    output_dir = "app/static/reports"
    os.makedirs(output_dir, exist_ok=True)
    file_path = f"{output_dir}/ledger_{from_date}_to_{to_date}.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


def generate_property_geojson_export(db: Session) -> str:
    """Export all properties with geometry to GeoJSON file using GeoPandas."""
    properties = db.query(Property).filter(Property.geom.isnot(None)).all()

    data = []
    geometries = []
    for prop in properties:
        shape = to_shape(prop.geom)
        geometries.append(shape)
        data.append({
            "property_id": str(prop.property_id),
            "property_code": prop.property_code,
            "property_name": prop.property_name,
            "property_type": prop.property_type,
            "address": prop.address,
            "city": prop.city,
            "suburb": prop.suburb,
            "status": prop.status,
        })

    gdf = gpd.GeoDataFrame(data, geometry=geometries, crs="EPSG:4326")
    output_dir = "app/static/reports"
    os.makedirs(output_dir, exist_ok=True)
    file_path = f"{output_dir}/properties_export.geojson"
    gdf.to_file(file_path, driver="GeoJSON")
    return file_path
