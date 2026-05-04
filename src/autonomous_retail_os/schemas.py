from pydantic import BaseModel, Field


class StoreCreate(BaseModel):
    name: str
    owner_name: str = ""
    phone: str = ""
    city: str = ""
    state: str = ""
    store_type: str = "autonomous_mini_market"
    upi_vpa: str = ""


class StoreRead(StoreCreate):
    id: str
    active: bool

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    store_id: str
    name: str
    sku: str = ""
    category: str = "general"
    unit: str = "piece"
    cost_price: float = 0.0
    selling_price: float = 0.0
    stock_quantity: float = 0.0
    low_stock_threshold: float = 5.0
    tax_percent: float = 0.0
    perishable: bool = False


class ProductRead(ProductCreate):
    id: str
    active: bool

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    store_id: str
    customer_ref: str = "walk_in"


class SessionRead(BaseModel):
    id: str
    store_id: str
    customer_ref: str
    status: str
    confidence_score: float

    model_config = {"from_attributes": True}


class VisionEventCreate(BaseModel):
    store_id: str
    session_id: str = ""
    event_type: str
    product_id: str = ""
    quantity: float = 1.0
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "edge_simulator"
    payload: dict = Field(default_factory=dict)


class CartItemRead(BaseModel):
    id: str
    session_id: str
    product_id: str
    quantity: float
    unit_price: float
    confidence: float
    source: str

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    store_id: str
    session_id: str


class SaleRead(BaseModel):
    id: str
    store_id: str
    session_id: str
    subtotal: float
    tax_total: float
    total: float
    payment_status: str
    upi_payment_uri: str

    model_config = {"from_attributes": True}


class AgentDecisionRead(BaseModel):
    id: str
    store_id: str
    agent_name: str
    decision_type: str
    summary: str
    action_payload: str
    autonomous: bool
    confidence: float

    model_config = {"from_attributes": True}
