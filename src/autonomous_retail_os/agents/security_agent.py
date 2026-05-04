from autonomous_retail_os.agents.base import AgentContext, record_decision
from autonomous_retail_os.models import AgentDecision, EventType, StoreEvent
from autonomous_retail_os.services.cart_service import CartService


class SecurityAgent:
    name = "security_agent"

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type != EventType.CUSTOMER_EXITED.value or not event.session_id:
            return []
        items = CartService(context.db).get_items(event.session_id)
        if not items:
            return []
        decision = record_decision(
            context.db,
            store_id=context.store_id,
            agent_name=self.name,
            decision_type="exit_cart_payment_required",
            summary=f"Customer session {event.session_id} exited with {len(items)} cart items requiring payment verification",
            autonomous=True,
            confidence=event.confidence,
        )
        return [decision]
