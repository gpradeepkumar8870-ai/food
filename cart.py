from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db
from app.models import Cart, CartItem, MenuItem, Restaurant

cart_bp = Blueprint("cart", __name__)


def get_or_create_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.route("/")
@login_required
def view_cart():
    cart = get_or_create_cart()
    restaurant = Restaurant.query.get(cart.restaurant_id) if cart.restaurant_id else None
    return render_template("cart.html", cart=cart, restaurant=restaurant)


@cart_bp.route("/add/<int:menu_item_id>", methods=["POST"])
@login_required
def add_to_cart(menu_item_id):
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    cart = get_or_create_cart()

    # Enforce single-restaurant cart (standard food delivery UX)
    if cart.restaurant_id and cart.restaurant_id != menu_item.restaurant_id and cart.items:
        flash(
            "Your cart has items from another restaurant. Clear it first to order from a new restaurant.",
            "warning",
        )
        return redirect(url_for("main.restaurant_detail", restaurant_id=menu_item.restaurant_id))

    cart.restaurant_id = menu_item.restaurant_id

    existing = CartItem.query.filter_by(cart_id=cart.id, menu_item_id=menu_item.id).first()
    quantity = int(request.form.get("quantity", 1))

    if existing:
        existing.quantity += quantity
    else:
        db.session.add(CartItem(cart_id=cart.id, menu_item_id=menu_item.id, quantity=quantity))

    db.session.commit()
    flash(f"{menu_item.name} added to cart.", "success")
    return redirect(request.referrer or url_for("main.restaurant_detail", restaurant_id=menu_item.restaurant_id))


@cart_bp.route("/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("cart.view_cart"))

    action = request.form.get("action")
    if action == "increase":
        item.quantity += 1
    elif action == "decrease":
        item.quantity -= 1
        if item.quantity <= 0:
            db.session.delete(item)

    db.session.commit()
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from cart.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/clear", methods=["POST"])
@login_required
def clear_cart():
    cart = get_or_create_cart()
    for item in list(cart.items):
        db.session.delete(item)
    cart.restaurant_id = None
    db.session.commit()
    flash("Cart cleared.", "info")
    return redirect(url_for("cart.view_cart"))
