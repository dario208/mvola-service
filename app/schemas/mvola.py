from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MvolaTransactionCreate(BaseModel):
    amount: int
    descriptionText: str
    num_user: str
    user_id: int


class MvolaTransactionUpdate(BaseModel):
    transactionReference: str


class MvolaTransactionOut(BaseModel):
    id: int
    amount: int
    descriptionText: str
    requestDate: datetime
    originalTransactionReference: str
    transactionReference: Optional[str] = ""
    num_user: str
    currency: str
    x_correlation_id: str
    user_id: int
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
