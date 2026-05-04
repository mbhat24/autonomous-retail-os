from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from autonomous_retail_os.database import get_db
from autonomous_retail_os.schemas import CartItemRead
from autonomous_retail_os.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/{session_id}", response_model=list[CartItemRead])
def get_cart(session_id: str, db: Session = Depends(get_db)) -> list:
    return CartService(db).get_items(session_id)
