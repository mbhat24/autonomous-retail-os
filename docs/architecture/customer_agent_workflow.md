# Customer Agent Workflow

## Purpose

The Customer Agent interacts directly with shoppers through in-store chat, kiosk, voice, WhatsApp, or app UI.

## What It Can Do

- Welcome customer
- Find products
- Show cart
- Explain bill
- Provide UPI payment link
- Share receipt
- Guide customer to checkout
- Answer simple store questions

## API

Create customer:

```text
POST /customers
```

Chat with customer agent:

```text
POST /customers/chat
```

List session messages:

```text
GET /customers/messages/{session_id}
```

## Example Messages

Customer:

```text
show my cart
```

Agent:

```text
Your current cart:
Amul Milk 500ml x 2 = ₹56.00
Estimated total: ₹56.00
```

Customer:

```text
how to pay
```

Agent:

```text
Please pay ₹56.00 using this UPI link: upi://pay?...
```

Customer:

```text
find tomato
```

Agent:

```text
I found these products:
Tomato: ₹30.00, stock 23.5 kg
```

## Channels

The same agent can be connected to:

- In-store kiosk
- Mobile web app
- WhatsApp bot
- Voice assistant
- QR-based customer page

## Production Enhancements

Future versions should add:

- Local language responses
- Speech-to-text
- Text-to-speech
- WhatsApp Cloud API integration
- Personalized recommendations
- Complaint/refund flow
- Loyalty and offers
