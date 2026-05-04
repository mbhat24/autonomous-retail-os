from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from autonomous_retail_os.agents.orchestrator import AgentOrchestrator
from autonomous_retail_os.database import get_db
from autonomous_retail_os.schemas import AgentDecisionRead, VisionEventCreate

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/vision")
def ingest_vision_event(payload: VisionEventCreate, db: Session = Depends(get_db)) -> dict:
    event, decisions = AgentOrchestrator(db).ingest_event(**payload.model_dump())
    return {
        "event_id": event.id,
        "decisions": [AgentDecisionRead.model_validate(decision).model_dump() for decision in decisions],
    }
