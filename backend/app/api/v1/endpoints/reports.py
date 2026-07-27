import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.database import get_db
from app.api.deps import get_current_manager
from app.services.report_service import generate_monthly_report_excel, generate_property_geojson_export

router = APIRouter()


@router.get("/monthly")
def monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    property_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    """Generate monthly income/expense Excel report."""
    file_path = generate_monthly_report_excel(db, year, month, property_id)
    return FileResponse(file_path, filename=f"monthly_report_{year}_{month:02d}.xlsx")


@router.get("/properties/geojson")
def export_properties_geojson(
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    """Export all properties with geometry as GeoJSON file."""
    file_path = generate_property_geojson_export(db)
    return FileResponse(file_path, filename="properties_export.geojson")


@router.get("/payments")
def payment_ledger(
    from_date: date,
    to_date: date,
    lease_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    """Export payment ledger for date range."""
    from app.services.report_service import generate_payment_ledger_excel
    file_path = generate_payment_ledger_excel(db, from_date, to_date, lease_id)
    return FileResponse(file_path, filename=f"payment_ledger_{from_date}_to_{to_date}.xlsx")
