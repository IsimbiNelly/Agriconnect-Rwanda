from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Enum as SAEnum, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database.session import Base


# ── Enumerations ──────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    farmer = "farmer"
    buyer  = "buyer"
    admin  = "admin"


class ProductCategory(str, enum.Enum):
    grains     = "Grains"
    vegetables = "Vegetables"
    fruits     = "Fruits"
    dairy      = "Dairy"
    livestock  = "Livestock"
    other      = "Other"


class OrderStatus(str, enum.Enum):
    pending   = "pending"
    accepted  = "accepted"
    paid      = "paid"
    completed = "completed"
    rejected  = "rejected"


# ── User ──────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, index=True, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    full_name       = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(SAEnum(UserRole), nullable=False)
    location        = Column(String, nullable=True)
    phone           = Column(String, nullable=True)
    is_active       = Column(Boolean, default=True, nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)

    products      = relationship("Product",      back_populates="farmer", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user",   cascade="all, delete-orphan")


# ── Product ───────────────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id                 = Column(Integer, primary_key=True, index=True)
    name               = Column(String, index=True, nullable=False)
    description        = Column(Text, nullable=True)
    price_per_kg       = Column(Float, nullable=False)
    quantity_available = Column(Float, nullable=False)
    category           = Column(SAEnum(ProductCategory), nullable=False)
    location           = Column(String, nullable=False)
    image_url          = Column(String, nullable=True)
    is_active          = Column(Boolean, default=True)
    farmer_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at         = Column(DateTime, default=datetime.utcnow)
    updated_at         = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farmer  = relationship("User",   back_populates="products")
    ratings = relationship("Rating", back_populates="product", cascade="all, delete-orphan")


# ── Purchase Request ──────────────────────────────────────────────────────────

class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id               = Column(Integer, primary_key=True, index=True)
    buyer_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    farmer_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id       = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity         = Column(Float, nullable=False)
    total_price      = Column(Float, nullable=False)
    status           = Column(SAEnum(OrderStatus), default=OrderStatus.pending)
    note             = Column(Text, nullable=True)
    # Payment fields
    payment_ref      = Column(String, nullable=True)
    payment_phone    = Column(String, nullable=True)
    payment_name     = Column(String, nullable=True)
    payment_provider = Column(String, nullable=True)   # MTN | Airtel
    paid_at          = Column(DateTime, nullable=True)
    delivery_date    = Column(String, nullable=True)   # ISO date string
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    buyer   = relationship("User",    foreign_keys=[buyer_id])
    farmer  = relationship("User",    foreign_keys=[farmer_id])
    product = relationship("Product")


# ── Message ───────────────────────────────────────────────────────────────────

class Message(Base):
    __tablename__ = "messages"

    id          = Column(Integer, primary_key=True, index=True)
    sender_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content     = Column(Text, nullable=False)
    is_read     = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    sender   = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


# ── Rating ────────────────────────────────────────────────────────────────────

class Rating(Base):
    __tablename__ = "ratings"

    id         = Column(Integer, primary_key=True, index=True)
    buyer_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating     = Column(Integer, nullable=False)   # 0–10
    review     = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("buyer_id", "product_id", name="uq_buyer_product_rating"),
    )

    buyer   = relationship("User",    foreign_keys=[buyer_id])
    product = relationship("Product", back_populates="ratings")


# ── Notification ──────────────────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String, nullable=False)
    body       = Column(Text, nullable=False)
    ntype      = Column(String, default="info")   # product|order|message|transaction|admin
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
