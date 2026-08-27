from flask import Blueprint, render_template, request

from app.models import Restaurant, MenuItem

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured = Restaurant.query.filter_by(is_active=True).order_by(Restaurant.rating.desc()).limit(6).all()
    cuisines = sorted({r.cuisine_type for r in Restaurant.query.all() if r.cuisine_type})
    return render_template("index.html", restaurants=featured, cuisines=cuisines)


@main_bp.route("/restaurants")
def restaurants():
    cuisine = request.args.get("cuisine", "")
    search = request.args.get("q", "")

    query = Restaurant.query
    if cuisine:
        query = query.filter_by(cuisine_type=cuisine)
    if search:
        query = query.filter(Restaurant.name.ilike(f"%{search}%"))

    all_restaurants = query.order_by(Restaurant.rating.desc()).all()
    cuisines = sorted({r.cuisine_type for r in Restaurant.query.all() if r.cuisine_type})

    return render_template(
        "restaurants.html",
        restaurants=all_restaurants,
        cuisines=cuisines,
        selected_cuisine=cuisine,
        search=search,
    )


@main_bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    category = request.args.get("category", "")

    items_query = MenuItem.query.filter_by(restaurant_id=restaurant.id, is_available=True)
    if category:
        items_query = items_query.filter_by(category=category)

    menu_items = items_query.all()
    categories = sorted(
        {m.category for m in MenuItem.query.filter_by(restaurant_id=restaurant.id).all() if m.category}
    )

    return render_template(
        "restaurant_detail.html",
        restaurant=restaurant,
        menu_items=menu_items,
        categories=categories,
        selected_category=category,
    )


@main_bp.route("/about")
def about():
    return render_template("about.html")
