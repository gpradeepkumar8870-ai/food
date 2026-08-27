import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect

from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp
    from app.routes.delivery import delivery_bp
    from app.routes.restaurant import restaurant_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(delivery_bp, url_prefix="/delivery")
    app.register_blueprint(restaurant_bp, url_prefix="/restaurant-admin")

    # Template filters
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except (TypeError, ValueError):
            return value

    @app.template_filter("status_badge")
    def status_badge_filter(status):
        mapping = {
            "pending": "secondary",
            "confirmed": "info",
            "preparing": "warning",
            "ready": "primary",
            "out_for_delivery": "orange",
            "delivered": "success",
            "cancelled": "danger",
        }
        return mapping.get(status, "secondary")

    @app.context_processor
    def inject_globals():
        from app.models import CartItem
        from flask_login import current_user

        cart_count = 0
        if current_user.is_authenticated:
            cart_count = CartItem.query.join(
                CartItem.cart
            ).filter_by(user_id=current_user.id).count()
        return dict(cart_count=cart_count)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    with app.app_context():
        db.create_all()

    return app
