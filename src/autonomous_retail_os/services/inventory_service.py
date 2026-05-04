from sqlalchemy.orm import Session

from autonomous_retail_os.models import CartItem, Product, Sale


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def commit_sale_inventory(self, sale: Sale) -> None:
        items = self.db.query(CartItem).filter(CartItem.session_id == sale.session_id, CartItem.quantity > 0).all()
        for item in items:
            product = self.db.get(Product, item.product_id)
            if product is not None:
                product.stock_quantity = max(0.0, product.stock_quantity - item.quantity)
        self.db.commit()

    def low_stock_products(self, store_id: str) -> list[Product]:
        return (
            self.db.query(Product)
            .filter(
                Product.store_id == store_id,
                Product.active.is_(True),
                Product.stock_quantity <= Product.low_stock_threshold,
            )
            .all()
        )
