# Autonomous Retail OS

Autonomous Retail OS is a professional control plane for camera-assisted, UPI-first, autonomous retail stores in India.

The first implementation focuses on the software brain:

- Store onboarding
- Product catalog
- Customer sessions
- Camera/edge event ingestion
- Autonomous cart creation
- UPI checkout URI generation
- Payment confirmation simulation
- Inventory update
- Agent decisions for cart, inventory, replenishment, pricing, and security

## Vision

Build an India-scale autonomous supermarket/kirana/mini-market platform that can run with minimal human intervention using cameras, sensors, UPI payments, edge AI, and autonomous agents.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
retail-os server --reload
```

Open:

```text
http://127.0.0.1:8080/docs
```

## Demo Flow

Start the server, then run:

```bash
python scripts/demo_flow.py
```

## API Flow

1. Create store: `POST /stores`
2. Add product: `POST /products`
3. Start customer session: `POST /sessions`
4. Send camera event: `POST /events/vision`
5. Check cart: `GET /cart/{session_id}`
6. Checkout: `POST /checkout`
7. Confirm payment: `POST /checkout/{sale_id}/confirm-payment`
8. Review agent decisions: `GET /agents/decisions/{store_id}`

## Current Agent Set

- Vision Checkout Agent
- Security Agent
- Inventory Agent
- Replenishment Agent
- Pricing Agent

## GitHub Secret Safety

Never paste GitHub tokens or payment credentials into chat, code, docs, or commits. If a token was shared, revoke it immediately and use `gh auth login` or your local credential manager.
