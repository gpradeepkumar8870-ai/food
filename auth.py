from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.forms import RegistrationForm, LoginForm, ProfileForm
from app.models import User, Order

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("An account with this email already exists.", "danger")
            return render_template("register.html", form=form)
        if User.query.filter_by(username=form.username.data).first():
            flash("This username is already taken.", "danger")
            return render_template("register.html", form=form)

        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            address=form.address.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}!", "success")

            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            if user.role == "delivery_partner":
                return redirect(url_for("delivery.dashboard"))
            if user.role == "restaurant_owner":
                return redirect(url_for("restaurant.dashboard"))
            return redirect(url_for("main.index"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    recent_orders = (
        Order.query.filter_by(customer_id=current_user.id)
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template("profile.html", form=form, recent_orders=recent_orders)
