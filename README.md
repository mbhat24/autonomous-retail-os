# Autonomous Retail OS

Autonomous Retail OS is a fully AI-managed control plane for camera-assisted, UPI-first retail stores in India. Powered by Google Gemini, the AI agents run the entire store — cart management, inventory, replenishment, pricing, security, and customer service — with zero human intervention.

## AI Architecture

```
Camera/Edge Events → AgentOrchestrator
                        ↓
    ┌───────────────────┼───────────────────┐
    ↓                   ↓                   ↓
VisionCheckout    SecurityAgent       InventoryAgent
(cart updates)    (theft detection)   (low-stock alerts)
                        ↓                   ↓
                ReplenishmentAgent    PricingAgent
                (auto purchase orders)(dynamic discounts)
                        ↓
                CustomerAgent
                (in-store chat)
```

Each agent receives the full store context (products, stock, cart, session, sales) and uses Gemini to reason about what action to take. Every decision is recorded with the AI's reasoning and confidence score for full auditability.

## Setup

### 1. Get a Gemini API Key (Free)

Go to [Google AI Studio](https://aistudio.google.com) and click "Get API Key". The free tier is generous and sufficient for running a store.

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your key:

```env
GEMINI_API_KEY=your_actual_key_here
```

### 3. Install & Run

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

## AI Agents

| Agent | Role | Triggers |
|---|---|---|
| VisionCheckoutAgent | Applies item_picked/item_returned events to cart | `item_picked`, `item_returned` |
| SecurityAgent | Detects customers exiting without payment | `customer_exited` |
| InventoryAgent | Alerts when products drop below threshold | `payment_confirmed`, `stock_adjusted` |
| ReplenishmentAgent | Auto-drafts purchase orders for low stock | `payment_confirmed`, `stock_adjusted` |
| PricingAgent | Suggests discounts on excess perishable stock | `stock_adjusted`, `customer_exited` |
| CustomerAgent | Handles in-store customer chat | Any customer message |

All agents operate fully autonomously — every decision is executed immediately with `autonomous=true`.

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | Your Google Gemini API key (required) |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model to use |
| `DATABASE_URL` | `sqlite:///./retail_os.db` | Database connection string |
| `DEFAULT_UPI_PAYEE_VPA` | `merchant@upi` | Default UPI VPA for payments |
