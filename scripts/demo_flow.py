import requests

BASE = "http://127.0.0.1:8080"

store = requests.post(
    f"{BASE}/stores",
    json={"name": "Demo Autonomous Store", "city": "Bengaluru", "state": "Karnataka", "upi_vpa": "demo@upi"},
    timeout=10,
).json()
product = requests.post(
    f"{BASE}/products",
    json={
        "store_id": store["id"],
        "name": "Amul Milk 500ml",
        "sku": "MILK-500",
        "category": "dairy",
        "unit": "piece",
        "cost_price": 24,
        "selling_price": 28,
        "stock_quantity": 10,
        "low_stock_threshold": 5,
    },
    timeout=10,
).json()
session = requests.post(
    f"{BASE}/sessions",
    json={"store_id": store["id"], "customer_ref": "demo_customer"},
    timeout=10,
).json()
requests.post(
    f"{BASE}/events/vision",
    json={
        "store_id": store["id"],
        "session_id": session["id"],
        "event_type": "item_picked",
        "product_id": product["id"],
        "quantity": 2,
        "confidence": 0.96,
        "source": "camera_1_simulator",
    },
    timeout=10,
)
sale = requests.post(
    f"{BASE}/checkout",
    json={"store_id": store["id"], "session_id": session["id"]},
    timeout=10,
).json()
paid = requests.post(f"{BASE}/checkout/{sale['id']}/confirm-payment", timeout=10).json()
print({"store": store, "product": product, "session": session, "sale": paid})
