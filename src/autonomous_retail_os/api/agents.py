from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from autonomous_retail_os.database import get_db
from autonomous_retail_os.models import AgentDecision
from autonomous_retail_os.schemas import AgentDecisionRead

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/decisions/{store_id}", response_model=list[AgentDecisionRead])
def list_decisions(store_id: str, db: Session = Depends(get_db)) -> list[AgentDecision]:
    return (
        db.query(AgentDecision)
        .filter(AgentDecision.store_id == store_id)
        .order_by(AgentDecision.created_at.desc())
        .limit(100)
        .all()
    )
