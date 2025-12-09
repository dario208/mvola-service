from typing import Optional
from pydantic import BaseModel
from models.elecdis_model import Mvola_transaction

class Mvola_transaction_create(BaseModel):
    amount: int
    descriptionText: str
    num_user: str
    user_id: int

class Mvola_transaction_update(BaseModel):
    transactionReference: str