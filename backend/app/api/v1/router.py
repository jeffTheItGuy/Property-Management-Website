from fastapi import APIRouter

from app.api.v1.endpoints import landlords, properties, units, leases, payments, maintenance, reports, communications

api_router = APIRouter()

api_router.include_router(landlords.router, prefix="/landlords", tags=["landlords"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(units.router, prefix="/units", tags=["units"])
api_router.include_router(leases.router, prefix="/leases", tags=["leases"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(communications.router, prefix="/communications", tags=["communications"])

# Auth route inside landlords file or separate; keeping simple:
from app.api.v1.endpoints import auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
