from datetime import datetime

from sqlalchemy.orm import Session

from autonomous_retail_os.models import CartItem, EventType, Product, StoreEvent


class CartService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def apply_event(self, event: StoreEvent) -> None:
        if event.event_type not in {EventType.ITEM_PICKED.value, EventType.ITEM_RETURNED.value}:
            return
        if not event.session_id or not event.product_id:
            return
        product = self.db.get(Product, event.product_id)
        if product is None:
            return
        item = (
            self.db.query(CartItem)
            .filter(CartItem.session_id == event.session_id, CartItem.product_id == event.product_id)
            .one_or_none()
        )
        delta = event.quantity if event.event_type == EventType.ITEM_PICKED.value else -event.quantity
        if item is None and delta > 0:
            item = CartItem(
                session_id=event.session_id,
                product_id=event.product_id,
                quantity=delta,
                unit_price=product.selling_price,
                confidence=event.confidence,
                source=event.source,
            )
            self.db.add(item)
        elif item is not None:
            item.quantity = max(0.0, item.quantity + delta)
            item.confidence = min(item.confidence, event.confidence)
            item.updated_at = datetime.utcnow()
        self.db.commit()

    def get_items(self, session_id: str) -> list[CartItem]:
        return self.db.query(CartItem).filter(CartItem.session_id == session_id, CartItem.quantity > 0).all()
