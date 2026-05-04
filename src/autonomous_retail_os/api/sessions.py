from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from autonomous_retail_os.database import get_db
from autonomous_retail_os.models import CustomerSession, Store
from autonomous_retail_os.schemas import SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)) -> CustomerSession:
    if db.get(Store, payload.store_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="store not found")
    session = CustomerSession(**payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
