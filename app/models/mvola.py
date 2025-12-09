from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class MvolaTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: int
    description_text: str
    request_date: datetime
    original_transaction_reference: str
    transaction_reference: Optional[str] = ""
    num_user: str
    currency: str = "Ar"
    x_correlation_id: str
    user_id: int
    status: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
