import json
import logging
from typing import Any

import google.generativeai as genai

from autonomous_retail_os.agents.base import AgentContext, record_decision
from autonomous_retail_os.config import get_settings
from autonomous_retail_os.models import (
    AgentDecision,
    CartItem,
    CustomerSession,
    Product,
    Sale,
    Store,
    StoreEvent,
)

logger = logging.getLogger(__name__)

DECISION_SCHEMA = """
Return a JSON object with a "decisions" array. Each decision must have:
  - decision_type: string (short snake_case label)
  - summary: string (human-readable explanation of the reasoning)
  - action_payload: object (machine-readable data for downstream systems)
  - confidence: number between 0.0 and 1.0

Return {"decisions": []} if no action is needed.
"""


class LLMAgent:
    name: str = "llm_agent"
    system_prompt: str = "You are a retail operations AI agent."

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in environment or .env file")
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=self.system_prompt + "\n\n" + DECISION_SCHEMA,
        )
        self._settings = settings

    def handle_event(self, event: StoreEvent, context: AgentContext) -> list[AgentDecision]:
        store_context = self._build_context(event, context)
        if store_context is None:
            return []

        prompt = self._build_prompt(event, store_context)
        raw = self._call_llm(prompt)
        if raw is None:
            return []

        proposals = self._parse_response(raw)
        return self._validate_and_record(proposals, context)

    def _build_context(self, event: StoreEvent, context: AgentContext) -> dict[str, Any] | None:
        db = context.db
        store = db.get(Store, context.store_id)
        if store is None:
            return None

        products = (
            db.query(Product)
            .filter(Product.store_id == context.store_id, Product.active.is_(True))
            .all()
        )

        cart_items: list[dict[str, Any]] = []
        if event.session_id:
            items = (
                db.query(CartItem)
                .filter(CartItem.session_id == event.session_id, CartItem.quantity > 0)
                .all()
            )
            for item in items:
                product = db.get(Product, item.product_id)
                cart_items.append({
                    "product_id": item.product_id,
                    "product_name": product.name if product else "unknown",
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "confidence": item.confidence,
                })

        session = None
        if event.session_id:
            session = db.get(CustomerSession, event.session_id)

        recent_sale = None
        if event.session_id:
            recent_sale = (
                db.query(Sale)
                .filter(Sale.session_id == event.session_id)
                .order_by(Sale.created_at.desc())
                .first()
            )

        return {
            "store": {
                "id": store.id,
                "name": store.name,
                "city": store.city,
                "store_type": store.store_type,
            },
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "unit": p.unit,
                    "cost_price": p.cost_price,
                    "selling_price": p.selling_price,
                    "stock_quantity": p.stock_quantity,
                    "low_stock_threshold": p.low_stock_threshold,
                    "perishable": p.perishable,
                }
                for p in products
            ],
            "cart_items": cart_items,
            "session": {
                "id": session.id,
                "status": session.status,
                "customer_ref": session.customer_ref,
            } if session else None,
            "recent_sale": {
                "id": recent_sale.id,
                "total": recent_sale.total,
                "payment_status": recent_sale.payment_status,
            } if recent_sale else None,
        }

    def _build_prompt(self, event: StoreEvent, store_context: dict[str, Any]) -> str:
        event_data = {
            "event_type": event.event_type,
            "product_id": event.product_id,
            "quantity": event.quantity,
            "confidence": event.confidence,
            "source": event.source,
            "session_id": event.session_id,
            "payload": json.loads(event.payload) if event.payload else {},
        }
        return json.dumps({"event": event_data, "store_context": store_context}, indent=2)

    def _call_llm(self, prompt: str) -> str | None:
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception:
            logger.exception("Gemini API call failed for agent %s", self.name)
            return None

    def _parse_response(self, raw: str) -> list[dict[str, Any]]:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:]) if len(lines) > 1 else text
        if text.endswith("```"):
            text = text[: -3].strip()
        try:
            parsed = json.loads(text)
            return parsed.get("decisions", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON: %s", raw[:200])
            return []

    def _validate_and_record(
        self, proposals: list[dict[str, Any]], context: AgentContext
    ) -> list[AgentDecision]:
        decisions: list[AgentDecision] = []
        for proposal in proposals:
            decision_type = str(proposal.get("decision_type", ""))
            summary = str(proposal.get("summary", ""))
            action_payload = proposal.get("action_payload", {})
            ai_confidence = float(proposal.get("confidence", 0.5))

            if not decision_type or not summary:
                continue

            ai_confidence = max(0.0, min(1.0, ai_confidence))

            decisions.append(
                record_decision(
                    context.db,
                    store_id=context.store_id,
                    agent_name=self.name,
                    decision_type=decision_type,
                    summary=summary,
                    action_payload=json.dumps(action_payload),
                    autonomous=True,
                    confidence=ai_confidence,
                )
            )
        return decisions
