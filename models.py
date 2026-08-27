import random
import string
from datetime import datetime

from flask_login import UserMixin

from app import db, bcrypt


def generate_order_number():
    return "FD" + "".join(random.choices(string.digits, k=8))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text)
    role = db.Column(db.String(20), default="customer")  # customer, delivery_partner, restaurant_owner
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship(
        "Order", backref="customer", lazy=True, foreign_keys="Order.customer_id"
    )
    deliveries = db.relationship(
        "Order", backref="delivery_partner", lazy=True, foreign_keys="Order.delivery_partner_id"
    )
    restaurants = db.relationship("Restaurant", backref="owner", lazy=True)
    reviews = db.relationship("Review", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    image = db.Column(db.String(200))
    cuisine_type = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    opening_time = db.Column(db.String(10), default="09:00")
    closing_time = db.Column(db.String(10), default="23:00")
    rating = db.Column(db.Float, default=4.2)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    menu_items = db.relationship(
        "MenuItem", backref="restaurant", lazy=True, cascade="all, delete-orphan"
    )
    orders = db.relationship("Order", backref="restaurant", lazy=True)
    reviews = db.relationship("Review", backref="restaurant", lazy=True)

    @property
    def average_rating(self):
        if not self.reviews:
            return self.rating
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # Starters, Main Course, Desserts, Beverages
    image = db.Column(db.String(200))
    is_available = db.Column(db.Boolean, default=True)
    is_veg = db.Column(db.Boolean, default=True)
    preparation_time = db.Column(db.Integer, default=20)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_items = db.relationship("OrderItem", backref="menu_item", lazy=True)
    cart_items = db.relationship("CartItem", backref="menu_item", lazy=True)

    def __repr__(self):
        return f"<MenuItem {self.name}>"


class Order(db.Model):
    __tablename__ = "orders"

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, default=generate_order_number)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    subtotal = db.Column(db.Float, nullable=False, default=0)
    delivery_fee = db.Column(db.Float, nullable=False, default=0)
    tax_amount = db.Column(db.Float, nullable=False, default=0)
    total_amount = db.Column(db.Float, nullable=False)

    delivery_address = db.Column(db.Text, nullable=False)
    delivery_instructions = db.Column(db.Text)

    status = db.Column(db.String(20), default="pending")
    payment_method = db.Column(db.String(50), default="cod")  # cod, razorpay
    payment_status = db.Column(db.String(20), default="pending")  # pending, paid, failed
    razorpay_payment_id = db.Column(db.String(100))

    delivery_partner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    estimated_delivery_time = db.Column(db.DateTime)
    actual_delivery_time = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")
    review = db.relationship("Review", backref="order", uselist=False)

    STATUS_FLOW = ["pending", "confirmed", "preparing", "ready", "out_for_delivery", "delivered"]

    def next_status(self):
        if self.status in self.STATUS_FLOW:
            idx = self.STATUS_FLOW.index(self.status)
            if idx + 1 < len(self.STATUS_FLOW):
                return self.STATUS_FLOW[idx + 1]
        return None

    def progress_percent(self):
        if self.status == "cancelled":
            return 0
        if self.status in self.STATUS_FLOW:
            idx = self.STATUS_FLOW.index(self.status)
            return int((idx / (len(self.STATUS_FLOW) - 1)) * 100)
        return 0

    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)  # snapshot at order time
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # unit price snapshot
    special_instructions = db.Column(db.Text)

    @property
    def line_total(self):
        return round(self.price * self.quantity, 2)


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("CartItem", backref="cart", lazy=True, cascade="all, delete-orphan")

    @property
    def subtotal(self):
        return round(sum(ci.menu_item.price * ci.quantity for ci in self.items), 2)

    @property
    def total_items(self):
        return sum(ci.quantity for ci in self.items)


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    special_instructions = db.Column(db.Text)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def line_total(self):
        return round(self.menu_item.price * self.quantity, 2)


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    delivery_rating = db.Column(db.Integer, default=5)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
