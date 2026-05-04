from autonomous_retail_os.agents.base import AgentContext
from autonomous_retail_os.agents.llm_agent import LLMAgent
from autonomous_retail_os.models import AgentDecision, StoreEvent
from autonomous_retail_os.services.inventory_service import InventoryService


class ReplenishmentAgent(LLMAgent):
    name = "replenishment_agent"
    system_prompt = (
        "You are the Replenishment Agent for an autonomous retail store in India. "
        "Your job is to draft purchase orders for products that are low on stock.\n\n"
        "RULES:\n"
        "- Only act on payment_confirmed and stock_adjusted events.\n"
        "- Check all low-stock products (stock_quantity <= low_stock_threshold).\n"
        "- For each low-stock product, calculate a reorder quantity: max(low_stock_threshold * 3 - stock_quantity, low_stock_threshold).\n"
        "- Calculate estimated_cost = reorder_quantity * cost_price.\n"
        "- Include product_id, reorder_quantity, estimated_cost in action_payload.\n"
        "- If no products need reordering, return no decisions.\n\n"
        "Decision types to use: purchase_order_draft"
    )

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in ("payment_confirmed", "stock_adjusted"):
            return []
        low_stock = InventoryService(context.db).low_stock_products(context.store_id)
        if not low_stock:
            return []
        return super().handle_event(event, context)
