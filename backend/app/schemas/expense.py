import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExpenseCategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None
    is_active: bool = True


class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass


class ExpenseCategoryResponse(ExpenseCategoryBase):
    category_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExpenseBase(BaseModel):
    property_id: uuid.UUID
    unit_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    expense_type: str
    description: Optional[str] = None
    amount: float
    currency_code: str
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    paid_date: Optional[date] = None
    is_recoverable_from_tenant: bool = False


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    expense_type: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    currency_code: Optional[str] = None
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    paid_date: Optional[date] = None
    is_recoverable_from_tenant: Optional[bool] = None


class ExpenseResponse(ExpenseBase):
    expense_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
