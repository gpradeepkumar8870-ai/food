import random
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, current_app, jsonify, request
from flask_login import login_required, current_user

from app import db
from app.forms import CheckoutForm, ReviewForm
from app.models import Cart, Order, OrderItem, Review

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("main.restaurants"))

    restaurant = cart.items[0].menu_item.restaurant
    if not restaurant.is_active:
        flash(f"{restaurant.name} is currently closed. Please try another restaurant.", "danger")
        return redirect(url_for("main.restaurants"))

    form = CheckoutForm()
    if not form.delivery_address.data:
        form.delivery_address.data = current_user.address

    subtotal = cart.subtotal
    delivery_fee = current_app.config["DELIVERY_FEE"]
    tax_amount = round(subtotal * current_app.config["TAX_PERCENT"] / 100, 2)
    total = round(subtotal + delivery_fee + tax_amount, 2)

    if form.validate_on_submit():
        order = Order(
            customer_id=current_user.id,
            restaurant_id=restaurant.id,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            total_amount=total,
            delivery_address=form.delivery_address.data,
            delivery_instructions=form.delivery_instructions.data,
            payment_method=form.payment_method.data,
            payment_status="pending",
            estimated_delivery_time=datetime.utcnow() + timedelta(minutes=random.randint(30, 55)),
        )
        db.session.add(order)
        db.session.flush()  # get order.id before commit

        for ci in cart.items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    menu_item_id=ci.menu_item_id,
                    item_name=ci.menu_item.name,
                    quantity=ci.quantity,
                    price=ci.menu_item.price,
                    special_instructions=ci.special_instructions,
                )
            )

        if form.payment_method.data == "cod":
            order.status = "confirmed"
            for item in list(cart.items):
                db.session.delete(item)
            cart.restaurant_id = None
            db.session.commit()
            flash(f"Order {order.order_number} placed successfully! Pay cash on delivery.", "success")
            return redirect(url_for("orders.track_order", order_number=order.order_number))
        else:
            # Razorpay flow: order stays pending until payment is confirmed
            db.session.commit()
            return redirect(url_for("orders.pay", order_id=order.id))

    return render_template(
        "checkout.html",
        form=form,
        cart=cart,
        restaurant=restaurant,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax_amount=tax_amount,
        total=total,
    )


@orders_bp.route("/pay/<int:order_id>")
@login_required
def pay(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.index"))

    return render_template(
        "payment.html",
        order=order,
        razorpay_key_id=current_app.config["RAZORPAY_KEY_ID"],
        razorpay_enabled=current_app.config["RAZORPAY_ENABLED"],
        amount_paise=int(order.total_amount * 100),
    )


@orders_bp.route("/pay/<int:order_id>/confirm", methods=["POST"])
@login_required
def confirm_payment(order_id):
    """
    Confirms payment for an order.

    If RAZORPAY_ENABLED=true and real keys are configured, verify the
    payment signature here using the razorpay Python SDK before marking
    the order as paid. For demo/offline use, this simulates a successful
    payment so the flow can be tested without live Razorpay credentials.
    """
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id:
        return jsonify({"success": False, "message": "Not authorized"}), 403

    payment_id = request.form.get("razorpay_payment_id", "pay_demo_" + str(random.randint(100000, 999999)))

    order.payment_status = "paid"
    order.razorpay_payment_id = payment_id
    order.status = "confirmed"
    db.session.commit()

    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        for item in list(cart.items):
            db.session.delete(item)
        cart.restaurant_id = None
        db.session.commit()

    flash(f"Payment successful! Order {order.order_number} confirmed.", "success")
    return redirect(url_for("orders.track_order", order_number=order.order_number))


@orders_bp.route("/track/<order_number>")
@login_required
def track_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.customer_id != current_user.id and current_user.role not in (
        "delivery_partner",
        "restaurant_owner",
    ):
        flash("Not authorized to view this order.", "danger")
        return redirect(url_for("main.index"))

    return render_template("order_tracking.html", order=order)


@orders_bp.route("/history")
@login_required
def history():
    all_orders = (
        Order.query.filter_by(customer_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("order_history.html", orders=all_orders)


@orders_bp.route("/cancel/<int:order_id>", methods=["POST"])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("orders.history"))

    if order.status in ("pending", "confirmed"):
        order.status = "cancelled"
        db.session.commit()
        flash(f"Order {order.order_number} cancelled.", "info")
    else:
        flash("This order can no longer be cancelled.", "warning")

    return redirect(url_for("orders.history"))


@orders_bp.route("/review/<int:order_id>", methods=["GET", "POST"])
@login_required
def leave_review(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("orders.history"))

    if order.status != "delivered":
        flash("You can only review delivered orders.", "warning")
        return redirect(url_for("orders.history"))

    if order.review:
        flash("You already reviewed this order.", "info")
        return redirect(url_for("orders.history"))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            user_id=current_user.id,
            rating=int(form.rating.data),
            delivery_rating=int(form.delivery_rating.data),
            comment=form.comment.data,
        )
        db.session.add(review)
        db.session.commit()
        flash("Thanks for your review!", "success")
        return redirect(url_for("orders.history"))

    return render_template("review.html", form=form, order=order)
