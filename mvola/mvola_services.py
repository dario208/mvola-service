from api.mvola.mvola_models import Mvola_transaction_create, Mvola_transaction_update
from sqlmodel import Session
from models.elecdis_model import Mvola_transaction
from sqlmodel import Session, select
import logging
import requests
import os
from datetime import datetime
import uuid

def create_mv_transaction(mv: Mvola_transaction_create, session: Session):
    try:  
        x_correlation_id = str(uuid.uuid4())
        originalTransactionReference = str(uuid.uuid4())
        requestDate = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        mv_transaction = Mvola_transaction(
            amount=mv.amount,
            descriptionText=mv.descriptionText,
            requestDate=requestDate,
            originalTransactionReference=originalTransactionReference,
            num_user=mv.num_user,
            currency="Ar",
            transactionReference="",
            x_correlation_id=x_correlation_id,
            user_id=mv.user_id
        )
        session.add(mv_transaction)
        session.flush()
        logging.info(f"Transaction mvola envoyé: {mv_transaction}")
        
        session.commit()
        logging.info("Commit success")
        
        session.refresh(mv_transaction)
        logging.info(f"After refresh: {mv_transaction}")
        
        # Send transaction to Mvola API
        response = post_mv_transaction(mv_transaction, x_correlation_id)
        return {
            "transaction_id": mv_transaction.id,
            "response": response
        }
    
    except Exception as e:
        logging.error(f"Error in create_ms: {str(e)}", exc_info=True)
        session.rollback()
        return {"messageError": f"Error: {str(e)}"}
    
def update_mv_transaction(id_mv_transaction: int, mv: Mvola_transaction_update, session: Session):
    mv_transaction: Mvola_transaction = session.exec(select(Mvola_transaction)
                                                     .where(Mvola_transaction.id == id_mv_transaction)).first()
    
    if mv_transaction is None:
        raise Exception(f"Aucune transaction associé à un id {id_mv_transaction}")
    
    logging.info(f"Message reçu: {mv}")

    mv_transaction.transactionReference = mv.transactionReference

    logging.info(f"Message modifié: {mv_transaction}")
    session.add(mv_transaction)
    session.commit()
    session.refresh(mv_transaction)

    return f"Modification réussie: {mv_transaction}"

def get_mv_transaction_status(id_mv_transaction, serverCorrelationId: str, session: Session):
    mv_transaction: Mvola_transaction = session.exec(select(Mvola_transaction)
                                                     .where(Mvola_transaction.id == id_mv_transaction)).first()
    if mv_transaction is None:
        raise Exception(f"Aucune transaction associé à un id {id_mv_transaction}")
    
    num_user = mv_transaction.num_user
    x_correlation_id = mv_transaction.x_correlation_id
    logging.info(f"x_correlation_id: {x_correlation_id}")
    logging.info(f"num_user: {num_user}")

    url = f"https://pre-api.mvola.mg/mvola/mm/transactions/type/merchantpay/1.0.0/status/{serverCorrelationId}"

    access_token = os.getenv("MVOLA_ACCESS_TOKEN")
    partner_name = os.getenv("MVOLA_PARTNER_NAME")
    app_num = os.getenv("MVOLA_APP_NUM")

    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {access_token}",
        "Version": "1.0",
        "X-CorrelationID": x_correlation_id,
        "UserLanguage": "FR",
        "UserAccountIdentifier": f"msisdn;{app_num}", 
        "partnerName": partner_name,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }

    response = requests.get(url, headers=headers)
    return response.json()

def get_mv_transaction_details(transactionReference: str, session: Session):
    mv = session.exec(select(Mvola_transaction)
                     .where(Mvola_transaction.transactionReference == transactionReference)).first()
    if mv is None:
        raise Exception(f"Aucune transaction associé à un transactionReference {transactionReference}")
    
    url = f"https://pre-api.mvola.mg/mvola/mm/transactions/type/merchantpay/1.0.0/{transactionReference}"

    access_token = os.getenv("MVOLA_ACCESS_TOKEN")
    partner_name = os.getenv("MVOLA_PARTNER_NAME")
    app_num = os.getenv("MVOLA_APP_NUM")

    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {access_token}",
        "Version": "1.0",
        "X-CorrelationID": mv.x_correlation_id, 
        "UserLanguage": "FR",
        "UserAccountIdentifier": f"msisdn;{app_num}", 
        "partnerName": partner_name,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def post_mv_transaction(mv: Mvola_transaction, x_correlation_id: str):
    url = "https://pre-api.mvola.mg/mvola/mm/transactions/type/merchantpay/1.0.0"

    access_token = os.getenv("MVOLA_ACCESS_TOKEN")
    app_num = os.getenv("MVOLA_APP_NUM")
    debit_num = mv.num_user
    credit_num = os.getenv("MVOLA_CREDIT_NUM")

    logging.info(f"Debit number: {debit_num}")
    partner_name = os.getenv("MVOLA_PARTNER_NAME")
    logging.info(f"Credit number: {app_num}")
    logging.info(f"Partner name: {partner_name}")

    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {access_token}",
        "Version": "1.0",
        "X-CorrelationID": x_correlation_id, 
        "UserLanguage": "FR",
        "UserAccountIdentifier": f"msisdn;{app_num}", 
        "partnerName": partner_name,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    logging.info(f"descriptionText: {mv.descriptionText}")
    logging.info(f"date: {mv.requestDate}")
    logging.info(f"Original transaction reference: {mv.originalTransactionReference}")
    payload = {
        "amount": str(mv.amount),
        "currency": "Ar",
        "descriptionText": mv.descriptionText,
        "requestingOrganisationTransactionReference": f"{os.getenv('MVOLA_REQUESTING_ORGANISATION_TRANSACTION_REFERENCE')}",
        "requestDate": mv.requestDate, 
        "originalTransactionReference": mv.originalTransactionReference,
        "debitParty": [{
            "key": "msisdn", 
            "value": debit_num
        }],
        "creditParty": [{
            "key": "msisdn", 
            "value": credit_num
        }],
        "metadata": [{
            "key": "partnerName", 
            "value": partner_name
        }]
    }

    logging.info(f"Payload: {payload}")
    logging.info(f"Headers: {headers}")

    response = requests.post(url, headers=headers, json=payload)
    print(response)
    return response.json()

def get_all_transactions_by_user_id(user_id: str, session: Session):
    transactions = session.exec(select(Mvola_transaction)
                                .where(Mvola_transaction.user_id == user_id)).all()
    if not transactions:
        return {
            "status": "failed",
            "details": f"Aucune transaction trouvé pour l'utilisateur {user_id}"
        }
    
    return transactions

