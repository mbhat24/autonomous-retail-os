# Inventory Lifecycle

## How Inventory Goes Down

Inventory is not reduced when the camera first sees an item being picked. It is reduced only after payment is confirmed.

This avoids incorrect stock reduction when:

- A customer picks an item and returns it
- Computer vision makes a low-confidence detection
- A customer abandons checkout
- Payment fails

## End-to-End Flow

```text
1. Customer enters store
2. Camera/edge device detects item picked
3. Edge sends `item_picked` event
4. Vision Checkout Agent updates cart
5. Customer exits or asks for checkout
6. Billing Service generates bill and UPI URI
7. Payment Agent/payment gateway confirms payment
8. Inventory Service deducts sold quantity from stock
9. Inventory Agent checks low stock
10. Replenishment Agent drafts or auto-approves reorder within policy
```

## Example

Initial stock:

```text
Amul Milk 500ml = 10 pieces
```

Camera event:

```json
{
  "event_type": "item_picked",
  "product_id": "milk_500ml",
  "quantity": 2
}
```

Cart becomes:

```text
Amul Milk 500ml x 2
```

Stock is still:

```text
10 pieces
```

After payment confirmation:

```text
10 - 2 = 8 pieces
```

Now stock becomes:

```text
8 pieces
```

## Why This Matters

Autonomous stores need accurate stock and auditability. The cart can change many times during shopping, but inventory should reflect completed sales only.

## Vegetable/Kirana Case

For loose vegetables:

```text
Tomato stock = 25 kg
Customer buys = 1.5 kg
After payment = 23.5 kg
```

For packet goods:

```text
Maggi stock = 100 packets
Customer buys = 3 packets
After payment = 97 packets
```

## Replenishment Trigger

If stock falls below threshold:

```text
Milk stock = 4
Low stock threshold = 5
```

The Inventory Agent creates a low-stock decision and the Replenishment Agent creates a purchase order draft.
