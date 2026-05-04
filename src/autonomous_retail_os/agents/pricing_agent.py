import json

from autonomous_retail_os.agents.base import AgentContext, record_decision
from autonomous_retail_os.models import AgentDecision, EventType, Product, StoreEvent


class PricingAgent:
    name = "pricing_agent"

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in {EventType.STOCK_ADJUSTED.value, EventType.CUSTOMER_EXITED.value}:
            return []
        products = (
            context.db.query(Product)
            .filter(Product.store_id == context.store_id, Product.perishable.is_(True), Product.active.is_(True))
            .all()
        )
        decisions: list[AgentDecision] = []
        for product in products:
            if product.stock_quantity > product.low_stock_threshold * 3 and product.selling_price > 0:
                suggested_price = round(product.selling_price * 0.95, 2)
                decisions.append(
                    record_decision(
                        context.db,
                        store_id=context.store_id,
                        agent_name=self.name,
                        decision_type="perishable_discount_suggestion",
                        summary=f"Suggest reducing {product.name} to {suggested_price} to clear perishable stock",
                        action_payload=json.dumps(
                            {"product_id": product.id, "suggested_price": suggested_price}
                        ),
                        autonomous=True,
                        confidence=0.82,
                    )
                )
        return decisions
