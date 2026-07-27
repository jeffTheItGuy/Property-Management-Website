import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SmsLogBase(BaseModel):
    recipient_type: str
    recipient_id: Optional[uuid.UUID] = None
    phone: str
    message: str
    status: str = "PENDING"
    sent_at: Optional[datetime] = None


class SmsLogCreate(SmsLogBase):
    pass


class SmsLogResponse(SmsLogBase):
    sms_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
