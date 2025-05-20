from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
import requests

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/transactions/", response_model=schemas.TransactionOut)
def create_transaction(txn: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # Fetch account details from account-service
    account_url = f"http://account-service:8000/accounts/{txn.account_id}"
    response = requests.get(account_url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Account not found")

    account = response.json()
    current_balance = account["balance"]

    # Debit check
    if txn.type == "debit" and txn.amount > current_balance:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Update account balance
    if txn.type == "credit":
        new_balance = current_balance + txn.amount
    elif txn.type == "debit":
        new_balance = current_balance - txn.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # Call PATCH to update balance
    update_url = f"http://account-service:8000/accounts/{txn.account_id}/balance"
    update_response = requests.patch(update_url, json={"balance": new_balance})
    if update_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update balance")

    # Store transaction
    db_txn = models.Transaction(**txn.dict())
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn

@router.get("/transactions/{txn_id}", response_model=schemas.TransactionOut)
def get_transaction(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).get(txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn
