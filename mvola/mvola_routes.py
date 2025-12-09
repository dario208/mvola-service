from fastapi import APIRouter, Depends
from core.database import get_session
from sqlalchemy.orm import Session
from api.mvola.mvola_services import get_all_transactions_by_user_id, create_mv_transaction, update_mv_transaction, get_mv_transaction_status, get_mv_transaction_details
from api.mvola.mvola_models import Mvola_transaction_create, Mvola_transaction_update
from models.elecdis_model import Mvola_transaction
from sqlmodel import Session, select
router = APIRouter()

@router.post("/create")
def create_mvola_transaction(mv: Mvola_transaction_create, session: Session=Depends(get_session)):
    try:
        return create_mv_transaction(mv=mv, session=session)
    except Exception as e:
        raise e

@router.post("/update/{id_mv_transaction}")   
def update_mvola_transaction(id_mv_transaction: int, mv: Mvola_transaction_update, session: Session=Depends(get_session)):
    try:
        return update_mv_transaction(id_mv_transaction=id_mv_transaction, mv=mv, session=session)
    except Exception as e:
        raise e

@router.get("/get-details/{transactionReference}")
def get_mvola_transaction_details(transactionReference: str, session: Session=Depends(get_session)):
    try:
        return get_mv_transaction_details(transactionReference=transactionReference, session=session)
    except Exception as e:
        raise e
    
@router.get("/get-status/{serverCorrelationId}")
def get_mvola_transaction_status(id_mv_transaction: str, serverCorrelationId: str, session: Session=Depends(get_session)):
    try:
        return get_mv_transaction_status(id_mv_transaction=id_mv_transaction, serverCorrelationId=serverCorrelationId, session=session)
    except Exception as e:
        raise e
    
@router.get("/get-all/{user_id}")
def get_all_mvola_transactions(user_id: str, session: Session=Depends(get_session)):
    try:
        return get_all_transactions_by_user_id(user_id=user_id, session=session)
    except Exception as e:
        raise e