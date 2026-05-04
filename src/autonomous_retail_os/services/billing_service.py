from sqlalchemy.orm import Session

from autonomous_retail_os.config import get_settings
from autonomous_retail_os.models import CartItem, PaymentStatus, Product, Sale, Store
from autonomous_retail_os.upi.qr import build_upi_uri


class BillingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def checkout(self, store_id: str, session_id: str) -> Sale:
        store = self.db.get(Store, store_id)
        if store is None:
            raise ValueError("store not found")
        items = self.db.query(CartItem).filter(CartItem.session_id == session_id, CartItem.quantity > 0).all()
        subtotal = 0.0
        tax_total = 0.0
        for item in items:
            product = self.db.get(Product, item.product_id)
            if product is None:
                continue
            line_subtotal = item.quantity * item.unit_price
            line_tax = line_subtotal * product.tax_percent / 100
            subtotal += line_subtotal
            tax_total += line_tax
        total = round(subtotal + tax_total, 2)
        sale = Sale(
            store_id=store_id,
            session_id=session_id,
            subtotal=round(subtotal, 2),
            tax_total=round(tax_total, 2),
            total=total,
            payment_status=PaymentStatus.PENDING.value,
        )
        self.db.add(sale)
        self.db.flush()
        sale.upi_payment_uri = build_upi_uri(
            payee_vpa=store.upi_vpa or self.settings.default_upi_payee_vpa,
            payee_name=store.name or self.settings.default_upi_payee_name,
            amount=total,
            transaction_note=f"RetailOS sale {sale.id}",
            transaction_ref=sale.id,
            currency=self.settings.default_currency,
        )
        self.db.commit()
        self.db.refresh(sale)
        return sale
