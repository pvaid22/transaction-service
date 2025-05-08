from pydantic import BaseModel

class TransactionCreate(BaseModel):
    account_id: int
    amount: int
    type: str  # 'credit' or 'debit'

class TransactionOut(TransactionCreate):
    id: int
    class Config:
        orm_mode = True