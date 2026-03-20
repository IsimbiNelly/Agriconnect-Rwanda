#!/usr/bin/env python3

import uuid
from datetime import datetime
from enum import Enum
from database.base import Base

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship, declarative_base

# ENUMS
class PurchaseStatus(str, Enum):
    pending = "pending"
    failed = "failed"
    completed = "completed"


def generate_uuid():
    return str(uuid.uuid4())


# FARMERS TABLE
class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmers_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20))

    password = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("ProductList", back_populates="farmer")

    transactions = relationship(
        "Transaction",
        back_populates="farmer"
    )

    purchase_requests = relationship(
        "PurchaseRequest",
        back_populates="farmer"
    )

    information = relationship(
        "FarmerInformation",
        back_populates="farmer",
        uselist=False
    )


# BUYERS TABLE
class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    buyer_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    phone_number = Column(String(20))

    password = Column(String(255), nullable=False)

    country = Column(String(100))
    city = Column(String(100))
    location = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship(
        "Transaction",
        back_populates="buyer"
    )

    purchase_requests = relationship(
        "PurchaseRequest",
        back_populates="buyer"
    )


# ADMINS TABLE
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# FARMER EXTRA INFORMATION
class FarmerInformation(Base):
    __tablename__ = "farmer_information"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)

    address = Column(String(255))
    country = Column(String(100))
    city = Column(String(100))

    farm_size = Column(Float)

    crops_grown = Column(Text)

    profile_picture = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="information")


# PRODUCT LIST
class ProductList(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    product_name = Column(String(255), nullable=False)
    product_category = Column(String(255))

    price_per_kilo = Column(Float, nullable=False)

    location_address = Column(String(255))

    status = Column(Boolean, default=True)

    farmer_id = Column(Integer, ForeignKey("farmers.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="products")

    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )


# PRODUCT IMAGES
class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(500), nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("ProductList", back_populates="images")


# PURCHASE REQUEST
class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purcharse_request_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    product_name = Column(String(255))

    quantity_requested = Column(Float)

    price = Column(Float)

    status = Column(SQLEnum(PurchaseStatus), default=PurchaseStatus.pending)

    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    buyer_id = Column(Integer, ForeignKey("buyers.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="purchase_requests")

    buyer = relationship("Buyer", back_populates="purchase_requests")


# TRANSACTIONS
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    product_name = Column(String(255))

    quantity = Column(Float)

    total_price = Column(Float)

    transaction_mode = Column(String(100))

    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    buyer_id = Column(Integer, ForeignKey("buyers.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="transactions")

    buyer = relationship("Buyer", back_populates="transactions")


# NOTIFICATIONS
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    notification_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    message = Column(Text)

    type = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# MESSAGES
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    sender_email = Column(String(255))
    receiver_email = Column(String(255))

    content = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ACTIVITY LOG
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_log_id = Column(String, unique=True, default=generate_uuid, nullable=False)

    user_email = Column(String(255))

    activity = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow)
