from pydantic import BaseModel, Field, field_validator
from datetime import date
from decimal import Decimal
from typing import Optional

class TransactionCreate(BaseModel):
    category_id: str
    amount: Decimal = Field(gt=0)
    txn_date: date
    note: Optional[str] = None

    @field_validator("txn_date")
    @classmethod
    def no_future_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Không thể tạo giao dịch cho ngày trong tương lai")
        return value

class TransactionUpdate(BaseModel):
    category_id: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    txn_date: Optional[date] = None
    note: Optional[str] = None

    @field_validator("txn_date")
    @classmethod
    def no_future_date(cls, value: Optional[date]) -> date:
        if value is None:
            raise ValueError("Ngày giao dịch không được để trống")
        if value > date.today():
            raise ValueError("Không thể tạo giao dịch cho ngày trong tương lai")
        return value

class TransactionOut(BaseModel):
    id: str
    category_id: str
    amount: Decimal
    type: str
    txn_date: date
    note: Optional[str] = None

    class Config:
        from_attributes = True
