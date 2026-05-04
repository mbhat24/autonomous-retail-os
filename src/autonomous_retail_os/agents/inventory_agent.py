import json

from autonomous_retail_os.agents.base import AgentContext, record_decision
from autonomous_retail_os.models import AgentDecision, EventType, StoreEvent
from autonomous_retail_os.services.inventory_service import InventoryService


class InventoryAgent:
    name = "inventory_agent"

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in {EventType.PAYMENT_CONFIRMED.value, EventType.STOCK_ADJUSTED.value}:
            return []
        low_stock = InventoryService(context.db).low_stock_products(context.store_id)
        decisions: list[AgentDecision] = []
        for product in low_stock:
            decisions.append(
                record_decision(
                    context.db,
                    store_id=context.store_id,
                    agent_name=self.name,
                    decision_type="low_stock_alert",
                    summary=f"{product.name} is low on stock: {product.stock_quantity} {product.unit}",
                    action_payload=json.dumps({"product_id": product.id, "stock": product.stock_quantity}),
                    autonomous=True,
                    confidence=0.98,
                )
            )
        return decisions
