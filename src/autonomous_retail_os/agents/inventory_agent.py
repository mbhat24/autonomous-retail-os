from autonomous_retail_os.agents.base import AgentContext
from autonomous_retail_os.agents.llm_agent import LLMAgent
from autonomous_retail_os.models import AgentDecision, StoreEvent
from autonomous_retail_os.services.inventory_service import InventoryService


class InventoryAgent(LLMAgent):
    name = "inventory_agent"
    system_prompt = (
        "You are the Inventory Agent for an autonomous retail store in India. "
        "Your job is to monitor stock levels and alert when products run low.\n\n"
        "RULES:\n"
        "- Only act on payment_confirmed and stock_adjusted events.\n"
        "- Check all active products for low stock (stock_quantity <= low_stock_threshold).\n"
        "- For each low-stock product, generate a low_stock_alert decision.\n"
        "- Include the product name, current stock, threshold, and unit in the summary.\n"
        "- If no products are low on stock, return no decisions.\n"
        "- Prioritize perishable items with higher urgency.\n\n"
        "Decision types to use: low_stock_alert"
    )

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in ("payment_confirmed", "stock_adjusted"):
            return []
        low_stock = InventoryService(context.db).low_stock_products(context.store_id)
        if not low_stock:
            return []
        return super().handle_event(event, context)
