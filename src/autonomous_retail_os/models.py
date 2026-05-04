from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class Unit(str, Enum):
    PIECE = "piece"
    KG = "kg"
    GRAM = "gram"
    LITER = "liter"
    ML = "ml"
    PACKET = "packet"
    BUNCH = "bunch"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class EventType(str, Enum):
    CUSTOMER_ENTERED = "customer_entered"
    ITEM_PICKED = "item_picked"
    ITEM_RETURNED = "item_returned"
    WEIGHT_READING = "weight_reading"
    CUSTOMER_EXITED = "customer_exited"
    PAYMENT_CONFIRMED = "payment_confirmed"
    STOCK_ADJUSTED = "stock_adjusted"


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("store"))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(160), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    city: Mapped[str] = mapped_column(String(80), default="")
    state: Mapped[str] = mapped_column(String(80), default="")
    store_type: Mapped[str] = mapped_column(String(80), default="autonomous_mini_market")
    upi_vpa: Mapped[str] = mapped_column(String(120), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    products: Mapped[list["Product"]] = relationship(back_populates="store")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("prod"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    sku: Mapped[str] = mapped_column(String(80), default="")
    category: Mapped[str] = mapped_column(String(80), default="general")
    unit: Mapped[str] = mapped_column(String(24), default=Unit.PIECE.value)
    cost_price: Mapped[float] = mapped_column(Float, default=0.0)
    selling_price: Mapped[float] = mapped_column(Float, default=0.0)
    stock_quantity: Mapped[float] = mapped_column(Float, default=0.0)
    low_stock_threshold: Mapped[float] = mapped_column(Float, default=5.0)
    tax_percent: Mapped[float] = mapped_column(Float, default=0.0)
    perishable: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    store: Mapped[Store] = relationship(back_populates="products")


class CustomerSession(Base):
    __tablename__ = "customer_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("session"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    customer_ref: Mapped[str] = mapped_column(String(120), default="walk_in")
    status: Mapped[str] = mapped_column(String(40), default="active")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("cust"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    preferred_language: Mapped[str] = mapped_column(String(40), default="en")
    upi_vpa: Mapped[str] = mapped_column(String(120), default="")
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CustomerMessage(Base):
    __tablename__ = "customer_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("msg"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String, default="")
    customer_id: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String(24), nullable=False)
    channel: Mapped[str] = mapped_column(String(40), default="in_store_chat")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("cartitem"))
    session_id: Mapped[str] = mapped_column(ForeignKey("customer_sessions.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str] = mapped_column(String(80), default="agent")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("sale"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(ForeignKey("customer_sessions.id"), nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    tax_total: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    payment_status: Mapped[str] = mapped_column(String(40), default=PaymentStatus.PENDING.value)
    upi_payment_uri: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("decision"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    decision_type: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    action_payload: Mapped[str] = mapped_column(Text, default="{}")
    autonomous: Mapped[bool] = mapped_column(Boolean, default=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StoreEvent(Base):
    __tablename__ = "store_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("event"))
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String, default="")
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    product_id: Mapped[str] = mapped_column(String, default="")
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str] = mapped_column(String(120), default="edge_simulator")
    payload: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("audit"))
    store_id: Mapped[str] = mapped_column(String, default="")
    actor: Mapped[str] = mapped_column(String(120), default="system")
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    details: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
