from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.core.security import decode_token
from app.models.stakeholders import PropertyManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_manager(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> PropertyManager:
    payload = decode_token(token)
    manager_id = payload.get("sub")
    if manager_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    manager = db.query(PropertyManager).filter(PropertyManager.manager_id == manager_id).first()
    if manager is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found")
    return manager
