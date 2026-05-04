from autonomous_retail_os.agents.base import AgentContext, record_decision
from autonomous_retail_os.models import AgentDecision, EventType, StoreEvent
from autonomous_retail_os.services.cart_service import CartService


class VisionCheckoutAgent:
    name = "vision_checkout_agent"

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in {EventType.ITEM_PICKED.value, EventType.ITEM_RETURNED.value}:
            return []
        CartService(context.db).apply_event(event)
        decision = record_decision(
            context.db,
            store_id=context.store_id,
            agent_name=self.name,
            decision_type="cart_updated",
            summary=f"Applied {event.event_type} for product {event.product_id} quantity {event.quantity}",
            confidence=event.confidence,
        )
        return [decision]
