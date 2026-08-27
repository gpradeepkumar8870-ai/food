from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.forms import RestaurantForm, MenuItemForm
from app.models import Restaurant, MenuItem, Order

restaurant_bp = Blueprint("restaurant", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != "restaurant_owner":
            abort(403)
        return f(*args, **kwargs)

    return decorated


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@restaurant_bp.route("/dashboard")
@login_required
@owner_required
def dashboard():
    my_restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
    incoming_orders = []
    if my_restaurants:
        restaurant_ids = [r.id for r in my_restaurants]
        incoming_orders = (
            Order.query.filter(
                Order.restaurant_id.in_(restaurant_ids),
                Order.status.in_(["confirmed", "preparing", "ready"]),
            )
            .order_by(Order.created_at.asc())
            .all()
        )
    return render_template("restaurant_dashboard.html", restaurants=my_restaurants, orders=incoming_orders)


@restaurant_bp.route("/create", methods=["GET", "POST"])
@login_required
@owner_required
def create_restaurant():
    form = RestaurantForm()
    if form.validate_on_submit():
        restaurant = Restaurant(
            name=form.name.data,
            description=form.description.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            cuisine_type=form.cuisine_type.data,
            opening_time=form.opening_time.data,
            closing_time=form.closing_time.data,
            is_active=form.is_active.data,
            owner_id=current_user.id,
            image=f"images/restaurants/placeholder_{(restaurant_placeholder_index())}.png",
        )
        db.session.add(restaurant)
        db.session.commit()
        flash(f"Restaurant '{restaurant.name}' created!", "success")
        return redirect(url_for("restaurant.dashboard"))
    return render_template("restaurant_form.html", form=form, title="Add Restaurant")


def restaurant_placeholder_index():
    return (Restaurant.query.count() % 6) + 1


@restaurant_bp.route("/<int:restaurant_id>/edit", methods=["GET", "POST"])
@login_required
@owner_required
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.owner_id != current_user.id:
        abort(403)

    form = RestaurantForm(obj=restaurant)
    if form.validate_on_submit():
        form.populate_obj(restaurant)
        db.session.commit()
        flash("Restaurant updated.", "success")
        return redirect(url_for("restaurant.dashboard"))
    return render_template("restaurant_form.html", form=form, title="Edit Restaurant")


@restaurant_bp.route("/<int:restaurant_id>/menu")
@login_required
@owner_required
def manage_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.owner_id != current_user.id:
        abort(403)
    return render_template("manage_menu.html", restaurant=restaurant)


@restaurant_bp.route("/<int:restaurant_id>/menu/add", methods=["GET", "POST"])
@login_required
@owner_required
def add_menu_item(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.owner_id != current_user.id:
        abort(403)

    form = MenuItemForm()
    if form.validate_on_submit():
        item = MenuItem(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            is_veg=form.is_veg.data,
            preparation_time=form.preparation_time.data,
            is_available=form.is_available.data,
            restaurant_id=restaurant.id,
            image=f"images/menu_items/placeholder_{(MenuItem.query.count() % 8) + 1}.png",
        )
        db.session.add(item)
        db.session.commit()
        flash(f"'{item.name}' added to menu.", "success")
        return redirect(url_for("restaurant.manage_menu", restaurant_id=restaurant.id))

    return render_template("menu_item_form.html", form=form, restaurant=restaurant, title="Add Menu Item")


@restaurant_bp.route("/menu/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@owner_required
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    if item.restaurant.owner_id != current_user.id:
        abort(403)

    form = MenuItemForm(obj=item)
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.commit()
        flash("Menu item updated.", "success")
        return redirect(url_for("restaurant.manage_menu", restaurant_id=item.restaurant_id))

    return render_template("menu_item_form.html", form=form, restaurant=item.restaurant, title="Edit Menu Item")


@restaurant_bp.route("/menu/<int:item_id>/delete", methods=["POST"])
@login_required
@owner_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    if item.restaurant.owner_id != current_user.id:
        abort(403)

    restaurant_id = item.restaurant_id
    db.session.delete(item)
    db.session.commit()
    flash("Menu item deleted.", "info")
    return redirect(url_for("restaurant.manage_menu", restaurant_id=restaurant_id))


@restaurant_bp.route("/order/<int:order_id>/advance", methods=["POST"])
@login_required
@owner_required
def advance_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.restaurant.owner_id != current_user.id:
        abort(403)

    # Restaurant owners can only advance orders through: confirmed -> preparing -> ready
    # (ready -> out_for_delivery is handled by a delivery partner accepting it)
    if order.status in ("confirmed", "preparing"):
        order.status = order.next_status()
        db.session.commit()
        flash(f"Order {order.order_number} moved to '{order.status}'.", "success")
    return redirect(url_for("restaurant.dashboard"))
