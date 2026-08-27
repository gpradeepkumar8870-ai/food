# FoodExpress — Food Delivery Application

A complete full-stack food delivery platform built with **Flask** and **MySQL** (SQLite by default for zero-setup use), as part of the *Free Online Python Full Stack Internship* task **PY-EC-002**.

## Features

| Feature | Status |
|---|---|
| User Authentication (Register/Login/Logout/Profile) | ✅ Flask-Login + Flask-Bcrypt |
| Restaurant Listings & Menus (with categories, cuisines, filters) | ✅ |
| Shopping Cart (add/update/remove, single-restaurant enforcement) | ✅ |
| Order Placement & Checkout | ✅ |
| Real-time Order Status Tracking (visual tracker) | ✅ pending → confirmed → preparing → ready → out for delivery → delivered |
| Delivery Partner Dashboard (accept orders, mark delivered) | ✅ |
| Restaurant Owner Dashboard (manage menu, advance order status) | ✅ |
| Payment Integration | ✅ Razorpay Checkout.js + Cash on Delivery |
| Rating & Reviews | ✅ Food + delivery rating after order is delivered |
| Auto-generated product/restaurant images | ✅ Pillow-generated placeholders (no external images needed) |
| One-click run scripts (Windows & Mac/Linux) | ✅ |

## Tech Stack

- **Backend:** Flask 3.x, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-WTF
- **Database:** SQLite by default (zero setup) — switch to MySQL 8.x with one environment variable
- **Frontend:** HTML5, Bootstrap 5, Font Awesome, vanilla JavaScript
- **Images:** Auto-generated with Pillow — no internet/image assets required
- **Payments:** Razorpay Checkout.js (test/demo mode works without real keys)

## Project Structure

```
food_delivery_app/
├── app/
│   ├── __init__.py          # App factory, blueprint registration
│   ├── models.py            # SQLAlchemy models
│   ├── forms.py              # WTForms
│   ├── routes/
│   │   ├── main.py           # Home, restaurant listing, menu browsing
│   │   ├── auth.py           # Register, login, logout, profile
│   │   ├── cart.py           # Cart management
│   │   ├── orders.py         # Checkout, payment, tracking, history, reviews
│   │   ├── delivery.py       # Delivery partner dashboard
│   │   └── restaurant.py     # Restaurant owner dashboard
│   ├── templates/            # Jinja2 templates (Bootstrap 5)
│   └── static/
│       ├── css/style.css
│       ├── js/script.js
│       └── images/           # Auto-generated placeholder images
├── config.py                 # App configuration (SQLite/MySQL, Razorpay)
├── run.py                    # App entry point
├── seed_data.py               # Demo data seeder
├── generate_images.py         # Pillow placeholder image generator
├── requirements.txt
├── run_windows.bat            # One-click setup + run (Windows)
├── run_mac_linux.sh           # One-click setup + run (Mac/Linux)
└── README.md
```

## Quick Start (Easiest — SQLite, zero setup)

### Windows
Double-click `run_windows.bat`, or from a terminal:
```
run_windows.bat
```

### Mac / Linux
```bash
chmod +x run_mac_linux.sh   # only needed once
./run_mac_linux.sh
```

Each script will:
1. Create a virtual environment
2. Install all dependencies
3. Generate placeholder restaurant/menu images
4. Seed the database with demo restaurants, menu items, and users
5. Start the app at **http://127.0.0.1:5000**

### Manual setup (any OS)
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python generate_images.py
python seed_data.py
python run.py
```

## Demo Login Credentials

After seeding, use these accounts to explore each role:

| Role | Email | Password |
|---|---|---|
| Customer | `customer@demo.com` | `password123` |
| Delivery Partner | `rider@demo.com` | `password123` |
| Restaurant Owner | `owner@demo.com` | `password123` |

Or register a new account and choose your role at signup.

## Switching to MySQL

The task specifies MySQL, and the app is fully compatible with it via SQLAlchemy. To switch:

1. Install MySQL Server and create the database:
   ```sql
   CREATE DATABASE food_delivery_db CHARACTER SET utf8mb4;
   CREATE USER 'food_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON food_delivery_db.* TO 'food_user'@'localhost';
   ```
2. Set the `DATABASE_URL` environment variable before running:
   ```bash
   # Linux / Mac
   export DATABASE_URL="mysql+pymysql://food_user:your_password@localhost/food_delivery_db"

   # Windows (cmd)
   set DATABASE_URL=mysql+pymysql://food_user:your_password@localhost/food_delivery_db
   ```
3. Run `python seed_data.py` then `python run.py` as usual.

`PyMySQL` (pure-Python MySQL driver) is already listed in `requirements.txt`, so no extra system dependencies (like `mysqlclient`'s C build tools) are required.

## Payment Integration (Razorpay)

- By default the app runs in **demo mode** (`RAZORPAY_ENABLED=false`), where the "Pay Online" checkout flow can be fully tested with a one-click "Simulate Successful Payment" button — no real keys needed.
- To use **live Razorpay test keys**:
  1. Get test keys from the [Razorpay Dashboard](https://dashboard.razorpay.com/app/keys)
  2. Set environment variables:
     ```bash
     export RAZORPAY_ENABLED=true
     export RAZORPAY_KEY_ID="rzp_test_xxxxxxxx"
     export RAZORPAY_KEY_SECRET="your_test_secret"
     ```
  3. Restart the app. Checkout will now open the real Razorpay payment widget.
- Cash on Delivery (COD) is also fully supported and requires no configuration.

## User Roles

- **Customer** — browse restaurants, order food, track orders, rate delivered orders.
- **Delivery Partner** — see orders marked "Ready," accept them, and mark as delivered.
- **Restaurant Owner** — add/edit restaurants, manage menu items, advance incoming orders through confirmed → preparing → ready.

## Order Status Flow

```
pending → confirmed → preparing → ready → out_for_delivery → delivered
                                                      ↘ cancelled (only from pending/confirmed)
```

- Customer places order → **pending**
- On COD confirmation or successful online payment → **confirmed**
- Restaurant owner marks **preparing** → **ready**
- Delivery partner accepts → **out_for_delivery**
- Delivery partner marks **delivered**

## Notes

- All restaurant and menu item images are auto-generated locally with Pillow (`generate_images.py`) — the app works fully offline with no external image dependencies, similar in spirit to the ShopEasy project's auto-generated product images.
- The database resets each time `seed_data.py` is run (`db.drop_all()` + `db.create_all()`), so it's safe to re-run for a clean demo state.
- `SECRET_KEY`, `RAZORPAY_KEY_ID`, and `RAZORPAY_KEY_SECRET` should be set via environment variables (not hardcoded) for any real deployment.

## Deployment

For deployment on PythonAnywhere/AWS/Heroku:
1. Set `DATABASE_URL`, `SECRET_KEY`, and Razorpay env vars in your host's config.
2. Run `python generate_images.py` and `python seed_data.py` once during deployment setup (or write your own production seed data).
3. Use a production WSGI server (e.g., `gunicorn run:app`) instead of Flask's built-in dev server.
4. Set `debug=False` in `run.py` for production.

---
Built for academic / internship submission purposes — free online Python full stack internship, Task ID PY-EC-002.
