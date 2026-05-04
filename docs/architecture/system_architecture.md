# System Architecture

## Goal

Autonomous Retail OS is designed as an event-driven autonomous store control plane.

## Production Architecture

```text
Cameras / Sensors / Scales / Entry QR
        |
        v
Edge AI Box
        |
        v
Store Event Stream
        |
        v
Autonomous Retail Backend
        |
        |-- Session Service
        |-- Cart Service
        |-- Billing Service
        |-- Payment Service
        |-- Inventory Service
        |-- Agent Orchestrator
        |-- Audit Service
        |-- Notification Service
        v
Central SaaS Dashboard
```

## Event-Driven Design

Every physical action becomes an event:

- `customer_entered`
- `item_picked`
- `item_returned`
- `weight_reading`
- `customer_exited`
- `payment_confirmed`
- `stock_adjusted`

Agents consume these events and produce auditable decisions.

## MVP Architecture

The MVP simulates edge camera events through `POST /events/vision`. This allows the autonomous store brain to be built before camera hardware is integrated.

## Production Database

Local development uses SQLite. Production should use PostgreSQL with managed backups, read replicas, and tenant-level isolation.

## Edge AI

The edge layer should run object detection, product recognition, person tracking, and sensor fusion locally to reduce latency and cloud cost.
