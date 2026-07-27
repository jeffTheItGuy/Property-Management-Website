from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.api.v1.router import api_router
from app.core.exceptions import add_exception_handlers

# Create tables on startup (dev convenience; use Alembic in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Zim Rental Manager",
    description="Low-tech property management for Zimbabwe",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Static files for uploads and generated receipts
app.mount("/uploads", StaticFiles(directory="app/static/uploads"), name="uploads")
app.mount("/receipts", StaticFiles(directory="app/static/receipts"), name="receipts")

add_exception_handlers(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}
