#!/usr/bin/env python3

import requests
from datetime import datetime

# Endpoint
url = "http://localhost:8000/articlesProduct/create"

# Farmer ID
farmer_id = "hffggi89434984"

# Current timestamp for created_at and updated_at
now = datetime.utcnow().isoformat() + "Z"

# Request body
payload = {
    "farmer_id": farmer_id,
    "product_name": "string",
    "product_category": "string",
    "price_per_kilo": 10,
    "location_address": "string",
    "status": True,
    "created_at": now,
    "updated_at": now
}

# POST request
response = requests.post(url, json=payload)

# Print response
print("Status Code:", response.status_code)
print("Response Body:", response.json())