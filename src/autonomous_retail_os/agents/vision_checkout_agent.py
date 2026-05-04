from autonomous_retail_os.agents.base import AgentContext
from autonomous_retail_os.agents.llm_agent import LLMAgent
from autonomous_retail_os.models import AgentDecision, StoreEvent
from autonomous_retail_os.services.cart_service import CartService


class VisionCheckoutAgent(LLMAgent):
    name = "vision_checkout_agent"
    system_prompt = (
        "You are the Vision Checkout Agent for an autonomous retail store in India. "
        "Your job is to process computer vision events (item_picked, item_returned) and update the customer's cart.\n\n"
        "RULES:\n"
        "- For item_picked events: add the item to the cart. If the item is already in the cart, increase quantity.\n"
        "- For item_returned events: decrease quantity, remove if quantity reaches 0.\n"
        "- Always check stock availability before adding items.\n"
        "- If stock is insufficient, flag a stock_mismatch_alert.\n"
        "- If vision confidence is low (<0.6), flag a low_confidence_cart_event.\n"
        "- For all other event types, return no decisions.\n\n"
        "Decision types to use: cart_updated, stock_mismatch_alert, low_confidence_cart_event"
    )

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type not in ("item_picked", "item_returned"):
            return []
        CartService(context.db).apply_event(event)
        return super().handle_event(event, context)
