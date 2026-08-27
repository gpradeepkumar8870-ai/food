from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import Order

delivery_bp = Blueprint("delivery", __name__)


def delivery_partner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != "delivery_partner":
            abort(403)
        return f(*args, **kwargs)

    return decorated


@delivery_bp.route("/dashboard")
@login_required
@delivery_partner_required
def dashboard():
    available_orders = (
        Order.query.filter_by(status="ready", delivery_partner_id=None)
        .order_by(Order.created_at.asc())
        .all()
    )
    my_active_orders = (
        Order.query.filter(
            Order.delivery_partner_id == current_user.id,
            Order.status.in_(["out_for_delivery"]),
        )
        .order_by(Order.created_at.asc())
        .all()
    )
    my_history = (
        Order.query.filter_by(delivery_partner_id=current_user.id, status="delivered")
        .order_by(Order.actual_delivery_time.desc())
        .limit(20)
        .all()
    )
    return render_template(
        "delivery_dashboard.html",
        available_orders=available_orders,
        my_active_orders=my_active_orders,
        my_history=my_history,
    )


@delivery_bp.route("/accept/<int:order_id>", methods=["POST"])
@login_required
@delivery_partner_required
def accept_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != "ready" or order.delivery_partner_id is not None:
        flash("This order is no longer available.", "warning")
        return redirect(url_for("delivery.dashboard"))

    order.delivery_partner_id = current_user.id
    order.status = "out_for_delivery"
    db.session.commit()
    flash(f"You accepted order {order.order_number}.", "success")
    return redirect(url_for("delivery.dashboard"))


@delivery_bp.route("/deliver/<int:order_id>", methods=["POST"])
@login_required
@delivery_partner_required
def mark_delivered(order_id):
    order = Order.query.get_or_404(order_id)
    if order.delivery_partner_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("delivery.dashboard"))

    order.status = "delivered"
    order.actual_delivery_time = datetime.utcnow()
    if order.payment_method == "cod":
        order.payment_status = "paid"
    db.session.commit()
    flash(f"Order {order.order_number} marked as delivered.", "success")
    return redirect(url_for("delivery.dashboard"))
