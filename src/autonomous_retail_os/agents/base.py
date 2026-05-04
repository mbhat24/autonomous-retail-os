from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.orm import Session

from autonomous_retail_os.models import AgentDecision, StoreEvent


@dataclass(frozen=True)
class AgentContext:
    db: Session
    store_id: str


class RetailAgent(Protocol):
    name: str

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        ...


def record_decision(
    db: Session,
    *,
    store_id: str,
    agent_name: str,
    decision_type: str,
    summary: str,
    action_payload: str = "{}",
    autonomous: bool = True,
    confidence: float = 1.0,
) -> AgentDecision:
    decision = AgentDecision(
        store_id=store_id,
        agent_name=agent_name,
        decision_type=decision_type,
        summary=summary,
        action_payload=action_payload,
        autonomous=autonomous,
        confidence=confidence,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision
