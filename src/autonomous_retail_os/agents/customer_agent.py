from sqlalchemy.orm import Session

from autonomous_retail_os.services.customer_service import CustomerService


class CustomerAgent:
    name = "customer_agent"

    def __init__(self, db: Session) -> None:
        self.service = CustomerService(db)

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
        normalized = message.lower().strip()
        suggested_actions: list[str] = []
        if any(word in normalized for word in ["cart", "bill", "total", "amount"]):
            reply = self._cart_reply(session_id)
            suggested_actions = ["checkout", "continue_shopping"]
        elif any(word in normalized for word in ["pay", "upi", "payment", "qr"]):
            reply = self._payment_reply(session_id)
            suggested_actions = ["open_upi_app", "show_qr", "call_support"]
        elif any(word in normalized for word in ["receipt", "invoice"]):
            reply = self._receipt_reply(session_id)
            suggested_actions = ["send_whatsapp_receipt", "download_invoice"]
        elif normalized.startswith("find ") or normalized.startswith("search "):
            query = normalized.replace("find ", "", 1).replace("search ", "", 1).strip()
            reply = self._product_reply(store_id, query)
            suggested_actions = ["add_to_cart", "ask_location"]
        else:
            store_name = self.service.store_name(store_id)
            reply = (
                f"Welcome to {store_name}. I can help you find products, check your cart, "
                "generate your bill, explain UPI payment, and share your receipt."
            )
            suggested_actions = ["find_product", "show_cart", "checkout"]
        self.service.record_message(
            store_id=store_id,
            session_id=session_id,
            customer_id=customer_id,
            role="agent",
            channel=channel,
            message=reply,
        )
        return reply, suggested_actions

    def _cart_reply(self, session_id: str) -> str:
        if not session_id:
            return "Please scan the store QR or start a shopping session so I can show your cart."
        lines, total = self.service.cart_summary(session_id)
        if not lines:
            return "Your cart is empty right now. Pick an item and I will add it automatically."
        return "Your current cart:\n" + "\n".join(lines) + f"\nEstimated total: ₹{total:.2f}"

    def _payment_reply(self, session_id: str) -> str:
        sale = self.service.latest_sale(session_id) if session_id else None
        if sale is None:
            return "Your bill is not generated yet. Please checkout first, then I will show the UPI payment link."
        if sale.payment_status == "paid":
            return f"Payment is already confirmed for bill {sale.id}. Thank you for shopping."
        return f"Please pay ₹{sale.total:.2f} using this UPI link: {sale.upi_payment_uri}"

    def _receipt_reply(self, session_id: str) -> str:
        sale = self.service.latest_sale(session_id) if session_id else None
        if sale is None:
            return "I cannot find a completed bill for this session yet."
        return f"Receipt {sale.id}: total ₹{sale.total:.2f}, payment status: {sale.payment_status}."

    def _product_reply(self, store_id: str, query: str) -> str:
        if not query:
            return "Tell me the product name you want to find. Example: find milk."
        products = self.service.product_search(store_id, query)
        if not products:
            return f"I could not find {query}. You can ask store support or try another product name."
        lines = [f"{p.name}: ₹{p.selling_price:.2f}, stock {p.stock_quantity:g} {p.unit}" for p in products]
        return "I found these products:\n" + "\n".join(lines)
