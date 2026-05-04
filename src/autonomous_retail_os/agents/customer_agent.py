import json
import logging

import google.generativeai as genai
from sqlalchemy.orm import Session

from autonomous_retail_os.config import get_settings
from autonomous_retail_os.services.customer_service import CustomerService

logger = logging.getLogger(__name__)


class CustomerAgent:
    name = "customer_agent"

    def __init__(self, db: Session) -> None:
        self.service = CustomerService(db)
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in environment or .env file")
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=(
                "You are a friendly, helpful customer service agent for an autonomous retail store in India. "
                "You help customers find products, check their cart, explain UPI payments, and share receipts. "
                "Respond in a warm, conversational tone. Keep responses concise.\n\n"
                "Return a JSON object with:\n"
                '  - reply: string (your response to the customer)\n'
                '  - suggested_actions: array of strings (2-3 relevant next actions)\n\n'
                "Suggested action options: checkout, continue_shopping, open_upi_app, show_qr, "
                "call_support, send_whatsapp_receipt, download_invoice, add_to_cart, ask_location, "
                "find_product, show_cart"
            ),
        )

    def reply(
        self,
        *,
        store_id: str,
        message: str,
        session_id: str = "",
        customer_id: str = "",
        channel: str = "in_store_chat",
    ) -> tuple[str, list[str]]:
        self.service.record_message(
            store_id=store_id,
            session_id=session_id,
            customer_id=customer_id,
            role="customer",
            channel=channel,
            message=message,
        )

        store_name = self.service.store_name(store_id)
        cart_lines, cart_total = self.service.cart_summary(session_id) if session_id else ([], 0.0)
        sale = self.service.latest_sale(session_id) if session_id else None

        context = {
            "store_name": store_name,
            "session_id": session_id,
            "cart": {"items": cart_lines, "total": cart_total} if cart_lines else None,
            "sale": {
                "id": sale.id,
                "total": sale.total,
                "payment_status": sale.payment_status,
                "upi_payment_uri": sale.upi_payment_uri,
            } if sale else None,
        }

        prompt = json.dumps({"customer_message": message, "context": context}, indent=2)

        try:
            response = self._model.generate_content(prompt)
            raw = response.text.strip()
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:]) if len(lines) > 1 else raw
            if raw.endswith("```"):
                raw = raw[:-3].strip()
            parsed = json.loads(raw)
            reply_text = parsed.get("reply", "I'm here to help! What would you like to do?")
            suggested_actions = parsed.get("suggested_actions", ["find_product", "show_cart"])
        except Exception:
            logger.exception("Gemini API call failed for customer_agent")
            reply_text = "I'm having trouble right now. Please try again or ask store support for help."
            suggested_actions = ["call_support"]

        self.service.record_message(
            store_id=store_id,
            session_id=session_id,
            customer_id=customer_id,
            role="agent",
            channel=channel,
            message=reply_text,
        )
        return reply_text, suggested_actions
