from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from autonomous_retail_os.database import get_db
from autonomous_retail_os.models import EventType, PaymentStatus, Sale
from autonomous_retail_os.schemas import CheckoutRequest, SaleRead
from autonomous_retail_os.services.billing_service import BillingService
from autonomous_retail_os.services.inventory_service import InventoryService
from autonomous_retail_os.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("", response_model=SaleRead)
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db)) -> Sale:
    return BillingService(db).checkout(payload.store_id, payload.session_id)


@router.post("/{sale_id}/confirm-payment", response_model=SaleRead)
def confirm_payment(sale_id: str, db: Session = Depends(get_db)) -> Sale:
    sale = db.get(Sale, sale_id)
    if sale is None:
        raise ValueError("sale not found")
    sale.payment_status = PaymentStatus.PAID.value
    db.commit()
    db.refresh(sale)
    InventoryService(db).commit_sale_inventory(sale)
    AgentOrchestrator(db).ingest_event(
        store_id=sale.store_id,
        session_id=sale.session_id,
        event_type=EventType.PAYMENT_CONFIRMED.value,
        source="payment_gateway_simulator",
    )
    db.refresh(sale)
    return sale
