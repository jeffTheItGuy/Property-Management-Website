from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.stakeholders import PropertyManager
from app.schemas.stakeholder import PropertyManagerResponse
from app.api.deps import get_current_manager

router = APIRouter()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    manager = db.query(PropertyManager).filter(PropertyManager.phone == form_data.username).first()
    if not manager or not verify_password(form_data.password, manager.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect phone or password")
    access_token = create_access_token(data={"sub": str(manager.manager_id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def register(
    full_name: str,
    national_id: str,
    phone: str,
    password: str,
    email: str = None,
    db: Session = Depends(get_db),
):
    existing = db.query(PropertyManager).filter(PropertyManager.phone == phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    manager = PropertyManager(
        full_name=full_name,
        national_id=national_id,
        phone=phone,
        email=email,
        password_hash=get_password_hash(password),
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return {"manager_id": manager.manager_id, "phone": manager.phone}


@router.get("/me", response_model=PropertyManagerResponse)
def get_me(
    current_manager: PropertyManager = Depends(get_current_manager),
):
    return current_manager