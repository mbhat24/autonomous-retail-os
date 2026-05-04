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
