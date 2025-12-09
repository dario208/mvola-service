from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.mvola import (
    MvolaTransactionCreate,
    MvolaTransactionOut,
    MvolaTransactionUpdate,
)
from app.services.mvola import (
    create_mv_transaction,
    get_all_transactions_by_user_id,
    get_mv_transaction_details,
    get_mv_transaction_status,
    update_mv_transaction,
)

router = APIRouter(prefix="/api/v1/mvola", tags=["mvola"])


@router.post("/create", response_model=dict)
def create_mvola_transaction(
    mv: MvolaTransactionCreate,
    session: Session = Depends(get_session),
):
    try:
        return create_mv_transaction(mv=mv, session=session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update/{id_mv_transaction}", response_model=MvolaTransactionOut)
def update_mvola_transaction(
    id_mv_transaction: int,
    mv: MvolaTransactionUpdate,
    session: Session = Depends(get_session),
):
    try:
        return update_mv_transaction(id_mv_transaction=id_mv_transaction, mv=mv, session=session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/details/{transactionReference}")
def get_mvola_transaction_details(
    transactionReference: str,
    session: Session = Depends(get_session),
):
    try:
        return get_mv_transaction_details(transactionReference=transactionReference, session=session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{serverCorrelationId}")
def get_mvola_transaction_status(
    serverCorrelationId: str,
    id_mv_transaction: int,
    session: Session = Depends(get_session),
):
    try:
        return get_mv_transaction_status(
            id_mv_transaction=id_mv_transaction,
            serverCorrelationId=serverCorrelationId,
            session=session,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}")
def get_all_mvola_transactions(
    user_id: int,
    session: Session = Depends(get_session),
):
    try:
        return get_all_transactions_by_user_id(user_id=user_id, session=session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
