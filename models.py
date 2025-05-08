from sqlalchemy import Column, Integer, String
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, index=True)
    amount = Column(Integer)
    type = Column(String)  # credit or debit