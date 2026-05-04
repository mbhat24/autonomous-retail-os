from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from autonomous_retail_os.database import get_db
from autonomous_retail_os.models import Product, Store
from autonomous_retail_os.schemas import ProductCreate, ProductRead

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductRead)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    if db.get(Store, payload.store_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="store not found")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/store/{store_id}", response_model=list[ProductRead])
def list_products(store_id: str, db: Session = Depends(get_db)) -> list[Product]:
    return db.query(Product).filter(Product.store_id == store_id, Product.active.is_(True)).all()
