from fastapi.testclient import TestClient

from autonomous_retail_os.main import app


def test_autonomous_checkout_flow() -> None:
    client = TestClient(app)
    store = client.post("/stores", json={"name": "Test Store", "upi_vpa": "test@upi"}).json()
    product = client.post(
        "/products",
        json={
            "store_id": store["id"],
            "name": "Tomato",
            "unit": "kg",
            "cost_price": 20,
            "selling_price": 30,
            "stock_quantity": 25,
            "low_stock_threshold": 5,
            "perishable": True,
        },
    ).json()
    session = client.post("/sessions", json={"store_id": store["id"]}).json()
    event_response = client.post(
        "/events/vision",
        json={
            "store_id": store["id"],
            "session_id": session["id"],
            "event_type": "item_picked",
            "product_id": product["id"],
            "quantity": 1.5,
            "confidence": 0.95,
        },
    ).json()
    assert event_response["decisions"]
    cart = client.get(f"/cart/{session['id']}").json()
    assert len(cart) == 1
    sale = client.post("/checkout", json={"store_id": store["id"], "session_id": session["id"]}).json()
    assert sale["total"] == 45.0
    assert sale["upi_payment_uri"].startswith("upi://pay?")
    paid = client.post(f"/checkout/{sale['id']}/confirm-payment").json()
    assert paid["payment_status"] == "paid"
    products_after_payment = client.get(f"/products/store/{store['id']}").json()
    assert products_after_payment[0]["stock_quantity"] == 23.5


def test_customer_agent_chat_flow() -> None:
    client = TestClient(app)
    store = client.post("/stores", json={"name": "Customer Agent Store", "upi_vpa": "agent@upi"}).json()
    product = client.post(
        "/products",
        json={
            "store_id": store["id"],
            "name": "Amul Milk 500ml",
            "unit": "piece",
            "selling_price": 28,
            "stock_quantity": 10,
        },
    ).json()
    session = client.post("/sessions", json={"store_id": store["id"], "customer_ref": "phone_999"}).json()
    client.post(
        "/events/vision",
        json={
            "store_id": store["id"],
            "session_id": session["id"],
            "event_type": "item_picked",
            "product_id": product["id"],
            "quantity": 2,
            "confidence": 0.97,
        },
    )
    cart_reply = client.post(
        "/customers/chat",
        json={"store_id": store["id"], "session_id": session["id"], "message": "show my cart"},
    ).json()
    assert "Amul Milk 500ml" in cart_reply["reply"]
    sale = client.post("/checkout", json={"store_id": store["id"], "session_id": session["id"]}).json()
    payment_reply = client.post(
        "/customers/chat",
        json={"store_id": store["id"], "session_id": session["id"], "message": "how to pay"},
    ).json()
    assert sale["upi_payment_uri"] in payment_reply["reply"]
