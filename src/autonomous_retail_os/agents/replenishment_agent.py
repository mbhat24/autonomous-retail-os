import json

from autonomous_retail_os.agents.base import AgentContext, record_decision
from autonomous_retail_os.config import get_settings
from autonomous_retail_os.models import AgentDecision, EventType, StoreEvent
from autonomous_retail_os.services.inventory_service import InventoryService


class ReplenishmentAgent:
    name = "replenishment_agent"

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in {EventType.PAYMENT_CONFIRMED.value, EventType.STOCK_ADJUSTED.value}:
            return []
        settings = get_settings()
        decisions: list[AgentDecision] = []
        for product in InventoryService(context.db).low_stock_products(context.store_id):
            reorder_qty = max(product.low_stock_threshold * 3 - product.stock_quantity, product.low_stock_threshold)
            estimated_cost = round(reorder_qty * product.cost_price, 2)
            autonomous = estimated_cost <= settings.auto_reorder_max_amount
            decisions.append(
                record_decision(
                    context.db,
                    store_id=context.store_id,
                    agent_name=self.name,
                    decision_type="purchase_order_draft",
                    summary=f"Draft reorder for {product.name}: {reorder_qty} {product.unit}, estimated cost {estimated_cost}",
                    action_payload=json.dumps(
                        {
                            "product_id": product.id,
                            "reorder_quantity": reorder_qty,
                            "estimated_cost": estimated_cost,
                            "auto_send_allowed": autonomous,
                        }
                    ),
                    autonomous=autonomous,
                    confidence=0.9,
                )
            )
        return decisions
