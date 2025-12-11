import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from sqlmodel import Session, select

from app.core.config import settings
from app.models.mvola_models import MvolaTransaction
from app.schemas.mvola import MvolaTransactionCreate, MvolaTransactionUpdate


def _format_request_date(dt: datetime) -> str:
    # Mvola expects millisecond precision with Zulu suffix
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _build_headers(x_correlation_id: str) -> Dict[str, str]:
    return {
        "Accept": "*/*",
        "Authorization": f"Bearer {settings.mvola_access_token}",
        "Version": "1.0",
        "X-CorrelationID": x_correlation_id,
        "UserLanguage": "FR",
        "UserAccountIdentifier": f"msisdn;{settings.mvola_app_num}",
        "partnerName": settings.mvola_partner_name,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }


def create_mv_transaction(mv: MvolaTransactionCreate, session: Session) -> Dict[str, Any]:
    try:
        x_correlation_id = str(uuid.uuid4())
        original_transaction_reference = str(uuid.uuid4())
        request_dt = datetime.utcnow()

        mv_transaction = MvolaTransaction(
            amount=mv.amount,
            description_text=mv.descriptionText,
            request_date=request_dt,
            original_transaction_reference=original_transaction_reference,
            num_user=mv.num_user,
            currency="Ar",
            transaction_reference="",
            x_correlation_id=x_correlation_id,
            user_id=mv.user_id,
        )
        session.add(mv_transaction)
        session.flush()

        logging.info("Transaction mvola créée en base: %s", mv_transaction)

        # Send transaction to Mvola API
        response = post_mv_transaction(mv_transaction)
        mv_transaction.updated_at = datetime.utcnow()
        session.add(mv_transaction)
        session.commit()
        session.refresh(mv_transaction)

        return {
            "transaction_id": mv_transaction.id,
            "response": response,
        }

    except Exception as e:
        logging.error("Error in create_mv_transaction: %s", e, exc_info=True)
        session.rollback()
        return {"messageError": f"Error: {str(e)}"}


def update_mv_transaction(id_mv_transaction: int, mv: MvolaTransactionUpdate, session: Session) -> MvolaTransaction:
    mv_transaction: Optional[MvolaTransaction] = session.exec(
        select(MvolaTransaction).where(MvolaTransaction.id == id_mv_transaction)
    ).first()

    if mv_transaction is None:
        raise Exception(f"Aucune transaction associée à l'id {id_mv_transaction}")

    mv_transaction.transaction_reference = mv.transactionReference
    mv_transaction.updated_at = datetime.utcnow()

    session.add(mv_transaction)
    session.commit()
    session.refresh(mv_transaction)

    return mv_transaction


def get_mv_transaction_status(id_mv_transaction: int, serverCorrelationId: str, session: Session) -> Dict[str, Any]:
    mv_transaction: Optional[MvolaTransaction] = session.exec(
        select(MvolaTransaction).where(MvolaTransaction.id == id_mv_transaction)
    ).first()
    if mv_transaction is None:
        raise Exception(f"Aucune transaction associée à l'id {id_mv_transaction}")

    url = f"https://pre-api.mvola.mg/mvola/mm/transactions/type/merchantpay/1.0.0/status/{serverCorrelationId}"
    headers = _build_headers(mv_transaction.x_correlation_id)

    response = requests.get(url, headers=headers, timeout=30)
    return response.json()


def get_mv_transaction_details(transactionReference: str, session: Session) -> Dict[str, Any]:
    mv_transaction: Optional[MvolaTransaction] = session.exec(
        select(MvolaTransaction).where(MvolaTransaction.transaction_reference == transactionReference)
    ).first()
    if mv_transaction is None:
        raise Exception(f"Aucune transaction associée au transactionReference {transactionReference}")

    url = f"https://pre-api.mvola.mg/mvola/mm/transactions/type/merchantpay/1.0.0/{transactionReference}"
    headers = _build_headers(mv_transaction.x_correlation_id)

    response = requests.get(url, headers=headers, timeout=30)
    return response.json()


def post_mv_transaction(mv: MvolaTransaction) -> Dict[str, Any]:
    url = "https://pre-api.mvola.mg/mvola/mm/transactions/type/merchantpay/1.0.0"

    headers = _build_headers(mv.x_correlation_id)
    payload = {
        "amount": str(mv.amount),
        "currency": mv.currency,
        "descriptionText": mv.description_text,
        "requestingOrganisationTransactionReference": settings.mvola_requesting_org_transaction_reference,
        "requestDate": _format_request_date(mv.request_date),
        "originalTransactionReference": mv.original_transaction_reference,
        "debitParty": [{"key": "msisdn", "value": mv.num_user}],
        "creditParty": [{"key": "msisdn", "value": settings.mvola_credit_num}],
        "metadata": [{"key": "partnerName", "value": settings.mvola_partner_name}],
    }

    logging.info("Payload Mvola: %s", payload)
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    return response.json()


def get_all_transactions_by_user_id(user_id: int, session: Session):
    transactions = session.exec(
        select(MvolaTransaction).where(MvolaTransaction.user_id == user_id)
    ).all()
    if not transactions:
        return {
            "status": "failed",
            "details": f"Aucune transaction trouvée pour l'utilisateur {user_id}",
        }

    return transactions
