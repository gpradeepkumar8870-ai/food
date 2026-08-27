"""
Populates the database with demo users, restaurants, and menu items so
the app is ready to explore immediately after setup.

Run with:  python seed_data.py
"""
from datetime import datetime, timedelta

from app import create_app, db
from app.models import User, Restaurant, MenuItem, Order, OrderItem, Review

RESTAURANTS_DATA = [
    {
        "name": "Spice Route",
        "cuisine_type": "Indian",
        "description": "Authentic North & South Indian cuisine made with traditional spices.",
        "address": "12 MG Road, Vellore, Tamil Nadu",
        "phone": "9876500001",
        "email": "contact@spiceroute.example",
        "image": "images/restaurants/placeholder_1.png",
        "rating": 4.5,
        "menu": [
            ("Paneer Butter Masala", "Cottage cheese in rich tomato gravy", 220, "Main Course", True),
            ("Chicken Biryani", "Fragrant basmati rice with spiced chicken", 260, "Main Course", False),
            ("Masala Dosa", "Crispy rice crepe with spiced potato filling", 120, "Starters", True),
            ("Gulab Jamun", "Warm milk dumplings in sugar syrup", 90, "Desserts", True),
            ("Masala Chai", "Spiced Indian tea", 40, "Beverages", True),
        ],
    },
    {
        "name": "Pizza Palazzo",
        "cuisine_type": "Italian",
        "description": "Wood-fired pizzas and fresh pastas made the Italian way.",
        "address": "45 Katpadi Road, Vellore, Tamil Nadu",
        "phone": "9876500002",
        "email": "hello@pizzapalazzo.example",
        "image": "images/restaurants/placeholder_2.png",
        "rating": 4.3,
        "menu": [
            ("Margherita Pizza", "Classic tomato, mozzarella & basil", 250, "Main Course", True),
            ("Pepperoni Pizza", "Loaded with spicy pepperoni", 320, "Main Course", False),
            ("Garlic Bread", "Oven-baked bread with garlic butter", 110, "Starters", True),
            ("Tiramisu", "Coffee-soaked Italian dessert", 150, "Desserts", True),
            ("Iced Lemon Tea", "Refreshing chilled lemon tea", 70, "Beverages", True),
        ],
    },
    {
        "name": "Green Bowl",
        "cuisine_type": "Healthy",
        "description": "Fresh salads, bowls, and smoothies for a healthy lifestyle.",
        "address": "8 Bagayam Main Road, Vellore, Tamil Nadu",
        "phone": "9876500003",
        "email": "info@greenbowl.example",
        "image": "images/restaurants/placeholder_3.png",
        "rating": 4.6,
        "menu": [
            ("Quinoa Buddha Bowl", "Quinoa, chickpeas, greens & tahini", 240, "Main Course", True),
            ("Grilled Chicken Salad", "Grilled chicken over mixed greens", 260, "Main Course", False),
            ("Sprouts Chaat", "Protein-rich sprouted moong chaat", 100, "Starters", True),
            ("Fresh Fruit Bowl", "Seasonal fruits with honey drizzle", 130, "Desserts", True),
            ("Green Detox Smoothie", "Spinach, apple & ginger smoothie", 120, "Beverages", True),
        ],
    },
    {
        "name": "Dragon Wok",
        "cuisine_type": "Chinese",
        "description": "Wok-tossed Indo-Chinese favorites, hot off the flame.",
        "address": "23 Gandhi Nagar, Vellore, Tamil Nadu",
        "phone": "9876500004",
        "email": "orders@dragonwok.example",
        "image": "images/restaurants/placeholder_4.png",
        "rating": 4.2,
        "menu": [
            ("Veg Hakka Noodles", "Stir-fried noodles with vegetables", 160, "Main Course", True),
            ("Chilli Chicken", "Spicy Indo-Chinese chicken stir-fry", 230, "Main Course", False),
            ("Spring Rolls", "Crispy vegetable spring rolls", 130, "Starters", True),
            ("Honey Noodles", "Crispy noodles tossed in honey glaze", 140, "Desserts", True),
            ("Lemon Iced Tea", "Chilled Chinese-style lemon tea", 65, "Beverages", True),
        ],
    },
    {
        "name": "Burger Barn",
        "cuisine_type": "American",
        "description": "Juicy burgers, crispy fries, and thick shakes.",
        "address": "56 Ida Scudder Road, Vellore, Tamil Nadu",
        "phone": "9876500005",
        "email": "hey@burgerbarn.example",
        "image": "images/restaurants/placeholder_5.png",
        "rating": 4.1,
        "menu": [
            ("Classic Veg Burger", "Crispy patty with fresh veggies", 140, "Main Course", True),
            ("Cheese Bacon Burger", "Beef-style patty with cheese & bacon", 220, "Main Course", False),
            ("Loaded Fries", "Fries topped with cheese & jalapenos", 130, "Starters", True),
            ("Chocolate Shake", "Thick chocolate milkshake", 110, "Desserts", True),
            ("Cola Float", "Cola with vanilla ice cream", 100, "Beverages", True),
        ],
    },
    {
        "name": "Curry House",
        "cuisine_type": "Indian",
        "description": "Home-style curries and comfort food, made fresh daily.",
        "address": "3 Officer's Line, Vellore, Tamil Nadu",
        "phone": "9876500006",
        "email": "support@curryhouse.example",
        "image": "images/restaurants/placeholder_6.png",
        "rating": 4.4,
        "menu": [
            ("Dal Tadka", "Yellow lentils tempered with spices", 140, "Main Course", True),
            ("Mutton Curry", "Slow-cooked mutton in spiced gravy", 320, "Main Course", False),
            ("Onion Bhaji", "Crispy onion fritters", 90, "Starters", True),
            ("Rasmalai", "Soft cottage cheese in sweet milk", 110, "Desserts", True),
            ("Buttermilk", "Spiced chilled buttermilk", 45, "Beverages", True),
        ],
    },
]

DEMO_USERS = [
    dict(username="customer_demo", email="customer@demo.com", phone="9000000001",
         address="101, Anna Nagar, Vellore, Tamil Nadu - 632001", role="customer", password="password123"),
    dict(username="rider_demo", email="rider@demo.com", phone="9000000002",
         address="55 Sathuvachari, Vellore, Tamil Nadu", role="delivery_partner", password="password123"),
    dict(username="owner_demo", email="owner@demo.com", phone="9000000003",
         address="Restaurant HQ, Vellore, Tamil Nadu", role="restaurant_owner", password="password123"),
    dict(username="admin", email="admin@demo.com", phone="9000000000",
         address="Admin Office", role="restaurant_owner", password="admin123"),
]


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Users ---
        users = {}
        for u in DEMO_USERS:
            user = User(
                username=u["username"],
                email=u["email"],
                phone=u["phone"],
                address=u["address"],
                role=u["role"],
            )
            user.set_password(u["password"])
            db.session.add(user)
            users[u["username"]] = user
        db.session.commit()

        owner = users["owner_demo"]

        # --- Restaurants + Menu Items ---
        restaurants = []
        for r in RESTAURANTS_DATA:
            restaurant = Restaurant(
                name=r["name"],
                description=r["description"],
                address=r["address"],
                phone=r["phone"],
                email=r["email"],
                image=r["image"],
                cuisine_type=r["cuisine_type"],
                rating=r["rating"],
                owner_id=owner.id,
                is_active=True,
                opening_time="09:00",
                closing_time="23:00",
            )
            db.session.add(restaurant)
            db.session.flush()

            for idx, (name, desc, price, category, is_veg) in enumerate(r["menu"]):
                item = MenuItem(
                    name=name,
                    description=desc,
                    price=price,
                    category=category,
                    is_veg=is_veg,
                    is_available=True,
                    preparation_time=15 + (idx * 5) % 25,
                    restaurant_id=restaurant.id,
                    image=f"images/menu_items/placeholder_{(idx % 8) + 1}.png",
                )
                db.session.add(item)

            restaurants.append(restaurant)

        db.session.commit()

        # --- Sample past order (delivered, reviewable) for the demo customer ---
        customer = users["customer_demo"]
        sample_restaurant = restaurants[0]
        sample_items = MenuItem.query.filter_by(restaurant_id=sample_restaurant.id).limit(2).all()

        subtotal = sum(i.price for i in sample_items)
        delivery_fee = 40.0
        tax = round(subtotal * 0.05, 2)
        total = round(subtotal + delivery_fee + tax, 2)

        past_order = Order(
            customer_id=customer.id,
            restaurant_id=sample_restaurant.id,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax_amount=tax,
            total_amount=total,
            delivery_address=customer.address,
            status="delivered",
            payment_method="cod",
            payment_status="paid",
            delivery_partner_id=users["rider_demo"].id,
            created_at=datetime.utcnow() - timedelta(days=2),
            actual_delivery_time=datetime.utcnow() - timedelta(days=2, hours=-1),
        )
        db.session.add(past_order)
        db.session.flush()

        for item in sample_items:
            db.session.add(
                OrderItem(
                    order_id=past_order.id,
                    menu_item_id=item.id,
                    item_name=item.name,
                    quantity=1,
                    price=item.price,
                )
            )
        db.session.commit()

        print("Database seeded successfully!\n")
        print("=" * 55)
        print("DEMO LOGIN CREDENTIALS")
        print("=" * 55)
        print("Customer         : customer@demo.com / password123")
        print("Delivery Partner : rider@demo.com     / password123")
        print("Restaurant Owner : owner@demo.com     / password123")
        print("=" * 55)
        print(f"Seeded {len(restaurants)} restaurants with menus.")


if __name__ == "__main__":
    seed()
