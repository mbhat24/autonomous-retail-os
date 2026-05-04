import json

from sqlalchemy.orm import Session

from autonomous_retail_os.agents.base import AgentContext
from autonomous_retail_os.agents.inventory_agent import InventoryAgent
from autonomous_retail_os.agents.pricing_agent import PricingAgent
from autonomous_retail_os.agents.replenishment_agent import ReplenishmentAgent
from autonomous_retail_os.agents.security_agent import SecurityAgent
from autonomous_retail_os.agents.vision_checkout_agent import VisionCheckoutAgent
from autonomous_retail_os.models import AgentDecision, StoreEvent


class AgentOrchestrator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.agents = [
            VisionCheckoutAgent(),
            SecurityAgent(),
            InventoryAgent(),
            ReplenishmentAgent(),
            PricingAgent(),
        ]

    def ingest_event(
        self,
        *,
        store_id: str,
        session_id: str,
        event_type: str,
        product_id: str = "",
        quantity: float = 1.0,
        confidence: float = 1.0,
        source: str = "edge_simulator",
        payload: dict | None = None,
    ) -> tuple[StoreEvent, list[AgentDecision]]:
        event = StoreEvent(
            store_id=store_id,
            session_id=session_id,
            event_type=event_type,
            product_id=product_id,
            quantity=quantity,
            confidence=confidence,
            source=source,
            payload=json.dumps(payload or {}),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        context = AgentContext(db=self.db, store_id=store_id)
        decisions: list[AgentDecision] = []
        for agent in self.agents:
            decisions.extend(agent.handle_event(event, context))
        return event, decisions
