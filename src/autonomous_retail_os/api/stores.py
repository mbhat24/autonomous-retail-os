from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from autonomous_retail_os.database import get_db
from autonomous_retail_os.models import Store
from autonomous_retail_os.schemas import StoreCreate, StoreRead

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=StoreRead)
def create_store(payload: StoreCreate, db: Session = Depends(get_db)) -> Store:
    store = Store(**payload.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.get("", response_model=list[StoreRead])
def list_stores(db: Session = Depends(get_db)) -> list[Store]:
    return db.query(Store).all()
