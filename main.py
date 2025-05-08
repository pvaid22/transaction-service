from fastapi import FastAPI
from routes import transaction
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(transaction.router)
