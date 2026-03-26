from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── Enumerations (mirror model enums) ────────────────────────────────────────

class UserRole(str, Enum):
    farmer = "farmer"
    buyer  = "buyer"
    admin  = "admin"


class ProductCategory(str, Enum):
    grains     = "Grains"
    vegetables = "Vegetables"
    fruits     = "Fruits"
    dairy      = "Dairy"
    livestock  = "Livestock"
    other      = "Other"


class OrderStatus(str, Enum):
    pending   = "pending"
    accepted  = "accepted"
    paid      = "paid"
    completed = "completed"
    rejected  = "rejected"


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username:  str
    email:     str
    full_name: str
    password:  str
    role:      UserRole
    location:  Optional[str] = None
    phone:     Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str
    role:     UserRole


class UserResponse(BaseModel):
    id:         int
    username:   str
    email:      str
    full_name:  str
    role:       UserRole
    location:   Optional[str] = None
    phone:      Optional[str] = None
    is_active:  bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type:   str
    user:         UserResponse


# ── Product ───────────────────────────────────────────────────────────────────

class FarmerInfo(BaseModel):
    id:        int
    username:  str
    full_name: str
    location:  Optional[str] = None
    phone:     Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id:                 int
    name:               str
    description:        Optional[str] = None
    price_per_kg:       float
    quantity_available: float
    category:           ProductCategory
    location:           str
    image_url:          Optional[str] = None
    is_active:          bool
    farmer_id:          int
    farmer:             FarmerInfo
    created_at:         datetime
    updated_at:         datetime
    avg_rating:         Optional[float] = None
    rating_count:       int = 0

    model_config = {"from_attributes": True}


# ── Orders ────────────────────────────────────────────────────────────────────

class PurchaseRequestCreate(BaseModel):
    product_id: int
    quantity:   float
    note:       Optional[str] = None


class BuyerInfo(BaseModel):
    id:        int
    username:  str
    full_name: str
    phone:     Optional[str] = None
    location:  Optional[str] = None

    model_config = {"from_attributes": True}


class ProductSnap(BaseModel):
    id:          int
    name:        str
    price_per_kg: float
    category:    ProductCategory
    image_url:   Optional[str] = None

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str


class PaymentRequest(BaseModel):
    phone:    str
    name:     str
    provider: str   # MTN | Airtel


class PurchaseRequestResponse(BaseModel):
    id:               int
    buyer_id:         int
    farmer_id:        int
    product_id:       int
    quantity:         float
    total_price:      float
    status:           OrderStatus
    note:             Optional[str] = None
    payment_ref:      Optional[str] = None
    payment_phone:    Optional[str] = None
    payment_name:     Optional[str] = None
    payment_provider: Optional[str] = None
    paid_at:          Optional[datetime] = None
    delivery_date:    Optional[str] = None
    created_at:       datetime
    updated_at:       datetime
    buyer:            BuyerInfo
    product:          ProductSnap

    model_config = {"from_attributes": True}


class ReceiptResponse(BaseModel):
    receipt_id:       str
    order_id:         int
    product_name:     str
    quantity:         float
    price_per_kg:     float
    total:            float
    payment_provider: str
    payment_phone:    str
    payment_name:     str
    paid_at:          str
    delivery_date:    str
    buyer_name:       str
    farmer_name:      str


# ── Messages ──────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    receiver_id: int
    content:     str


class MessageSenderInfo(BaseModel):
    id:        int
    username:  str
    full_name: str
    role:      UserRole

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id:          int
    sender_id:   int
    receiver_id: int
    content:     str
    is_read:     bool
    created_at:  datetime
    sender:      MessageSenderInfo
    receiver:    MessageSenderInfo

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    other_user:   MessageSenderInfo
    last_message: str
    last_at:      datetime
    unread_count: int


# ── Ratings ───────────────────────────────────────────────────────────────────

class RatingCreate(BaseModel):
    rating: int   # 0–10
    review: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: int) -> int:
        if not (0 <= v <= 10):
            raise ValueError("Rating must be between 0 and 10")
        return v


class RatingResponse(BaseModel):
    id:         int
    buyer_id:   int
    product_id: int
    rating:     int
    review:     Optional[str] = None
    created_at: datetime
    buyer:      BuyerInfo

    model_config = {"from_attributes": True}


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id:         int
    user_id:    int
    title:      str
    body:       str
    ntype:      str
    is_read:    bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminUserResponse(BaseModel):
    id:         int
    username:   str
    email:      str
    full_name:  str
    role:       UserRole
    location:   Optional[str] = None
    phone:      Optional[str] = None
    is_active:  bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PlatformStats(BaseModel):
    total_users:    int
    total_farmers:  int
    total_buyers:   int
    total_admins:   int
    active_users:   int
    inactive_users: int
    total_products: int
    active_products: int
    total_orders:   int
    pending_orders: int
    completed_orders: int
