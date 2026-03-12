#!/usr/bin/env python3

from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, AnyUrl, Field


class UserRole(str, Enum):
    farmer = "farmer"
    buyer = "buyer"
    admin = "admin"


class User(BaseModel):
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    email: EmailStr = Field(..., description="User email address")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    password: str = Field(..., min_length=6, description="User password")

    role: UserRole = Field(..., description="Role of the user")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FarmersMoreInformation(BaseModel):
    address: str = Field(..., description="Location Address of the farmer", example="Kigali")
    country: str = Field(..., description="Farmer's country", example="Rwanda")
    city: str = Field(..., description="Farmer's city", example="Kigali")

    farm_size: Optional[float] = Field(
        None,
        description="Size of the farm in hectares",
        example=5.0
    )

    crops_grown: List[str] = Field(
        ...,
        description="List of crops grown",
        example=["beans", "maize"]
    )

    profile_picture: AnyUrl = Field(
        ...,
        description="URL of the farmer's profile picture"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FarmersRegistration(User):
    role: UserRole = Field(default=UserRole.farmer)


class FarmersLogin(BaseModel):
    email: EmailStr = Field(..., description="Farmer email")
    password: str = Field(..., description="Farmer password")


class Buyers(User):
    country: str = Field(..., description="Buyer's country")
    city: str = Field(..., description="Buyer's city")
    location: str = Field(..., description="Buyer's address")

    role: UserRole = Field(default=UserRole.buyer)


class BuyersLogin(BaseModel):
    email: EmailStr = Field(..., description="Buyer email")
    password: str = Field(..., description="Buyer password")


class Admin(User):
    role: UserRole = Field(default=UserRole.admin)


class ProductList(BaseModel):
    product_name: str
    product_category: str
    price_per_kilo: float
    location_address: str

    status: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductImage(BaseModel):
    image_url: AnyUrl = Field(..., description="URL of the product image")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PurchaseStatus(str, Enum):
    pending = "pending"
    failed = "failed"
    completed = "completed"


class PurchaseRequest(BaseModel):
    product_name: str
    seller_first_name: str
    seller_last_name: str

    quantity_requested: float = Field(..., description="Quantity requested in Kg")

    price: Optional[float] = Field(
        None,
        description="Total price for the requested quantity"
    )

    status: PurchaseStatus = Field(
        default=PurchaseStatus.pending,
        description="Status of the purchase"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Transaction(BaseModel):
    product_name: str

    seller_first_name: str
    seller_last_name: str

    buyer_first_name: str
    buyer_last_name: str

    quantity: float = Field(..., description="Quantity in Kg")

    total_price: float = Field(..., description="Total price")

    transaction_mode: str = Field(
        ...,
        description="Transaction mode (Momo, bank transfer, cash)"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Notification(BaseModel):
    message: str

    type: str = Field(
        ...,
        description="Type of notification (order update, product listing)"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    sender_first_name: str
    sender_last_name: str
    sender_email: EmailStr = Field(..., description="Sender email")

    receiver_first_name: str
    receiver_last_name: str
    receiver_email: EmailStr = Field(..., description="Receiver email")

    content: str = Field(..., description="Message content")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ActivityLog(BaseModel):
    user_email: EmailStr = Field(..., description="User performing the activity")

    activity: str = Field(..., description="Activity description")

    timestamp: datetime = Field(default_factory=datetime.utcnow)
