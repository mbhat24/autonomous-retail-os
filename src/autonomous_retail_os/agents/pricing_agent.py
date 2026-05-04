from autonomous_retail_os.agents.base import AgentContext
from autonomous_retail_os.agents.llm_agent import LLMAgent
from autonomous_retail_os.models import AgentDecision, Product, StoreEvent


class PricingAgent(LLMAgent):
    name = "pricing_agent"
    system_prompt = (
        "You are the Pricing Agent for an autonomous retail store in India. "
        "Your job is to suggest dynamic pricing adjustments, especially for perishable goods.\n\n"
        "RULES:\n"
        "- Only act on stock_adjusted and customer_exited events.\n"
        "- Check all active perishable products with stock_quantity > low_stock_threshold * 3.\n"
        "- For each such product, suggest a 5% discount to clear excess perishable stock.\n"
        "- Calculate suggested_price = round(selling_price * 0.95, 2).\n"
        "- Include product_id, current_price, and suggested_price in action_payload.\n"
        "- If no perishable products need discounting, return no decisions.\n"
        "- Consider seasonality and demand patterns in your reasoning.\n\n"
        "Decision types to use: perishable_discount_suggestion"
    )

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in ("stock_adjusted", "customer_exited"):
            return []
        products = (
            context.db.query(Product)
            .filter(Product.store_id == context.store_id, Product.perishable.is_(True), Product.active.is_(True))
            .all()
        )
        if not any(p.stock_quantity > p.low_stock_threshold * 3 and p.selling_price > 0 for p in products):
            return []
        return super().handle_event(event, context)
