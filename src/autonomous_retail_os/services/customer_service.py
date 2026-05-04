from sqlalchemy.orm import Session

from autonomous_retail_os.models import CartItem, Customer, CustomerMessage, Product, Sale, Store


class CustomerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_customer(
        self,
        *,
        store_id: str,
        name: str = "",
        phone: str = "",
        preferred_language: str = "en",
        upi_vpa: str = "",
    ) -> Customer:
        customer = Customer(
            store_id=store_id,
            name=name,
            phone=phone,
            preferred_language=preferred_language,
            upi_vpa=upi_vpa,
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def record_message(
        self,
        *,
        store_id: str,
        role: str,
        message: str,
        session_id: str = "",
        customer_id: str = "",
        channel: str = "in_store_chat",
    ) -> CustomerMessage:
        row = CustomerMessage(
            store_id=store_id,
            session_id=session_id,
            customer_id=customer_id,
            role=role,
            channel=channel,
            message=message,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def cart_summary(self, session_id: str) -> tuple[list[str], float]:
        items = self.db.query(CartItem).filter(CartItem.session_id == session_id, CartItem.quantity > 0).all()
        lines: list[str] = []
        total = 0.0
        for item in items:
            product = self.db.get(Product, item.product_id)
            if product is None:
                continue
            line_total = round(item.quantity * item.unit_price, 2)
            total += line_total
            lines.append(f"{product.name} x {item.quantity:g} = ₹{line_total:.2f}")
        return lines, round(total, 2)

    def latest_sale(self, session_id: str) -> Sale | None:
        return (
            self.db.query(Sale)
            .filter(Sale.session_id == session_id)
            .order_by(Sale.created_at.desc())
            .first()
        )

    def product_search(self, store_id: str, query: str) -> list[Product]:
        return (
            self.db.query(Product)
            .filter(Product.store_id == store_id, Product.active.is_(True), Product.name.ilike(f"%{query}%"))
            .limit(5)
            .all()
        )

    def store_name(self, store_id: str) -> str:
        store = self.db.get(Store, store_id)
        return store.name if store else "this store"
