# AgriConnect

**AgriConnect** is a Rwandan agricultural marketplace that connects farmers directly to buyers. It provides role-based portals for Farmers, Buyers, and Admins, with real-time notifications, messaging, purchase transactions, mobile money payment simulation, product ratings, and a complete email notification system.

---

## Link to the app
https://agriconnect-rwanda.onrender.com/

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [User Roles & Portals](#user-roles--portals)
- [API Documentation](#api-documentation)
- [Author](#Author)
- [License](#License)

---

## Features

### Farmer Portal
- Register and manage a product catalogue (name, category, price in RWF, quantity in kg, location, image)
- Receive purchase requests from buyers and accept or reject them
- Mark orders as completed — product quantity is automatically reduced; product is marked unavailable when stock reaches 0
- Real-time notifications when a buyer submits a request or leaves a rating
- View each review and star rating submitted for their products in real time
- Message buyers directly via the in-app chat

### Buyer Portal
- Browse all active products with search and category filtering
- Send purchase requests with a custom note and desired quantity
- Simulate a Mobile Money (MTN / Airtel) payment on accepted orders
- Receive a receipt with delivery date after payment
- Rate products (0–10) and leave written reviews
- Real-time notifications for new products, order status changes, and messages

### Admin Portal
- View platform-wide statistics (users, products, orders)
- List, search, and filter all users by role and status
- Activate or deactivate any farmer or buyer account
- Deactivated users are blocked from logging in and from using the API

### All Portals
- Change password from within the dashboard (requires current password)
- Forgot password flow: enter email → receive 6-digit OTP → verify and set new password
- Welcome email sent on registration containing credentials
- Confirmation email sent after every password change

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI 0.115 |
| ORM | SQLAlchemy 2.0, SQLite |
| Validation | Pydantic v2, pydantic-settings |
| Auth | JWT (python-jose), bcrypt 4.2 |
| Real-time | FastAPI WebSockets |
| Email | Python smtplib (STARTTLS / Gmail SMTP) |
| Frontend | Vanilla HTML + CSS + JavaScript (no framework) |
| Server | Uvicorn (ASGI) |

---

## Project Structure

```
agriconnect/
├── backend/                         # Python package — all server-side code
│   ├── main.py                      # FastAPI app, routers, HTML page routes
│   ├── config/
│   │   └── settings.py              # Pydantic BaseSettings (reads .env)
│   ├── database/
│   │   └── session.py               # SQLAlchemy engine + get_db dependency
│   ├── model/
│   │   └── models.py                # ORM models (User, Product, PurchaseRequest, …)
│   ├── schema/
│   │   └── schemas.py               # Pydantic request/response schemas
│   ├── controllers/                 # Business logic layer
│   │   ├── auth_controller.py
│   │   ├── product_controller.py
│   │   ├── order_controller.py
│   │   ├── message_controller.py
│   │   └── admin_controller.py
│   ├── routers/                     # FastAPI routers (thin HTTP layer)
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── messages.py
│   │   ├── admin.py
│   │   └── ws.py                    # WebSocket endpoint
│   ├── services/
│   │   ├── auth_service.py          # Password hashing, JWT creation
│   │   ├── email_service.py         # SMTP email + HTML templates
│   │   ├── notification_service.py  # DB notifications + WebSocket push
│   │   └── otp_service.py           # In-memory OTP store (forgot password)
│   └── utils/
│       ├── auth.py                  # get_current_user, require_farmer/buyer/admin
│       └── ws_manager.py            # WebSocket ConnectionManager
├── static/
│   ├── css/
│   │   └── main.css
│   ├── js/
│   │   ├── config.js                # Shared utilities, modals, WebSocket helper
│   │   ├── auth.js                  # Login / register page logic
│   │   ├── farmer-dashboard.js
│   │   ├── farmer-products.js
│   │   ├── farmer-orders.js
│   │   ├── buyer-dashboard.js
│   │   ├── buyer-orders.js
│   │   ├── admin-dashboard.js
│   │   ├── admin-users.js
│   │   └── messages.js
│   ├── index.html                   # Login / register page
│   ├── farmer-dashboard.html
│   ├── farmer-products.html
│   ├── farmer-orders.html
│   ├── buyer-dashboard.html
│   ├── buyer-orders.html
│   ├── product-detail.html
│   ├── messages.html
│   ├── admin-dashboard.html
│   └── admin-users.html
├── .env                             # Environment variables (not committed)
├── requirements.txt
└── agriconnect.db                   # SQLite database (auto-created on first run)
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) enabled (for email features)

### Installation

```bash
# 1. Clone the repository

git clone https://github.com/IsimbiNelly/Agriconnect-Rwanda
cd Agriconnect-Rwanda

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file (see the section below)
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///./agriconnect.db

# JWT
SECRET_KEY=your-very-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=100000

# Email — Gmail SMTP with App Password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx       # create app password inside google manage account.
SMTP_FROM=AgriConnect <your-gmail@gmail.com>
```

> **Gmail App Password**: Go to Google Account → Security → 2-Step Verification → App passwords. Generate one for "Mail". Email features are optional — the app runs without SMTP configured, but the OTP-based password reset will not deliver codes.

---

## Running the App

```bash
# Run from the project root directory
uvicorn backend.main:app --port 8000 --reload
or
python -m backend.main
or python3 -m backend.main
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

The SQLite database and all tables are created automatically on first startup.

---

## User Roles & Portals

| Role | Registration | Dashboard |
|---|---|---|
| Farmer | Public self-registration | `/farmer/dashboard` |
| Buyer | Public self-registration | `/buyer/dashboard` |
| Admin | Public self-registration | `/admin/dashboard` |

All three roles register and log in from the same landing page (`/`). Select your role using the role buttons before submitting the form.

---

## API Documentation

Read the localhost:8000/docs or localhost/redoct to view the app documentation

## Author
```
Nelly Isimbi <i.assoumpta@alustudent.com>
```

## License
Protected
