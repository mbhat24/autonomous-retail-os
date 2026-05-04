from autonomous_retail_os.agents.base import AgentContext
from autonomous_retail_os.agents.llm_agent import LLMAgent
from autonomous_retail_os.models import AgentDecision, StoreEvent
from autonomous_retail_os.services.cart_service import CartService


class SecurityAgent(LLMAgent):
    name = "security_agent"
    system_prompt = (
        "You are the Security Agent for an autonomous retail store in India. "
        "Your job is to detect potential theft or payment issues when customers exit.\n\n"
        "RULES:\n"
        "- Only act on customer_exited events with a valid session_id.\n"
        "- Check the customer's cart items. If they have items but no payment was made, flag exit_cart_payment_required.\n"
        "- If the cart is empty, return no decisions.\n"
        "- If payment was already confirmed, return no decisions.\n"
        "- Assess risk based on cart value, number of items, and session confidence.\n\n"
        "Decision types to use: exit_cart_payment_required, security_alert, no_action"
    )

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        if event.event_type != "customer_exited" or not event.session_id:
            return []
        items = CartService(context.db).get_items(event.session_id)
        if not items:
            return []
        return super().handle_event(event, context)
