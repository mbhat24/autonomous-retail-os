from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from autonomous_retail_os.agents.customer_agent import CustomerAgent
from autonomous_retail_os.database import get_db
from autonomous_retail_os.models import Customer, CustomerMessage, Store
from autonomous_retail_os.schemas import (
    CustomerChatRequest,
    CustomerChatResponse,
    CustomerCreate,
    CustomerMessageRead,
    CustomerRead,
)
from autonomous_retail_os.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerRead)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> Customer:
    if db.get(Store, payload.store_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="store not found")
    return CustomerService(db).create_customer(**payload.model_dump())


@router.get("/store/{store_id}", response_model=list[CustomerRead])
def list_customers(store_id: str, db: Session = Depends(get_db)) -> list[Customer]:
    return db.query(Customer).filter(Customer.store_id == store_id).all()


@router.post("/chat", response_model=CustomerChatResponse)
def chat(payload: CustomerChatRequest, db: Session = Depends(get_db)) -> CustomerChatResponse:
    reply, suggested_actions = CustomerAgent(db).reply(**payload.model_dump())
    return CustomerChatResponse(reply=reply, suggested_actions=suggested_actions)


@router.get("/messages/{session_id}", response_model=list[CustomerMessageRead])
def list_messages(session_id: str, db: Session = Depends(get_db)) -> list[CustomerMessage]:
    return (
        db.query(CustomerMessage)
        .filter(CustomerMessage.session_id == session_id)
        .order_by(CustomerMessage.created_at.asc())
        .all()
    )
