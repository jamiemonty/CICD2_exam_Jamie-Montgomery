# app/main.py
from typing import Optional

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from .schemas import CustomerCreate, CustomerRead, OrderCreate, OrderRead, CustomerPatch
from .models import Base, CustomerDB, OrderDB

from app.database import engine, SessionLocal
from app.models import Base
#from app.schemas import 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev/exam). Prefer Alembic in production.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

def commit_or_rollback(db: Session, error_msg: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=error_msg)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


# ---- Health ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/customers", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session=Depends(get_db)):
    customer = CustomerDB(**payload.model_dump())
    db.add(customer)
    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    return customer

@app.get("/api/customers", response_model= list[CustomerRead])
def get_customers(db: Session=Depends(get_db)):
    stmt = select(CustomerDB).order_by(CustomerDB.id)
    return list(db.execute(stmt).scalars())

@app.get("/api/customers/{customer_id}", response_model=CustomerRead, status_code=200)
def get_customer(customer_id: int, db: Session=Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find customer with matching ID")

    return customer

@app.put("/api/customers/{customer_id}", response_model=CustomerRead)
def update_customer(customer_id: int, payload: CustomerCreate, db: Session=Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find customer with matching ID")
    
    customer.id = CustomerCreate.id
    customer.name = CustomerCreate.name
    customer.email = CustomerCreate.email
    customer.customer_since = CustomerCreate.customer_since

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    db.refresh(customer)
    return customer

@app.patch("/api/customers/{customer_id}", response_model=CustomerRead)
def patch_customer(customer_id:int, payload: CustomerPatch, db: Session=Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find customer with matching ID")

    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(proj, key, value)

    commit_or_rollback(db, "Couldn't update customer information")
    db.refresh(customer)
    return customer

@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(CustomerDB, customer_id)
    db.delete(customer)
    db.commit()
    return None

@app.post("/api/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session=Depends(get_db)):
    customer = db.get(UserDB, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find customer account")
    order = OrderDB(**payload.model_dump())
    db.add(order)
    commit_or_rollback(db, "Order creation failed")
    db.refresh(order)
    return customer

@app.get("/api/orders", response_model= list[OrderRead])
def get_orders(db: Session=Depends(get_db)):
    stmt = select(OrderDB).order_by(OrderDB.id)
    return list(db.execute(stmt).scalars())

@app.get("/api/customers/{order_id}", response_model=OrderRead, status_code=200)
def get_customer(order_id: int, db: Session=Depends(get_db)):
    order = db.get(OrderDB, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find order with matching ID")

    return order
