from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    SelectField,
    FloatField,
    IntegerField,
    BooleanField,
    SubmitField,
    RadioField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField("Address", validators=[Optional()])
    role = SelectField(
        "Register as",
        choices=[
            ("customer", "Customer"),
            ("delivery_partner", "Delivery Partner"),
            ("restaurant_owner", "Restaurant Owner"),
        ],
        default="customer",
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField("Address", validators=[Optional()])
    submit = SubmitField("Update Profile")


class CheckoutForm(FlaskForm):
    delivery_address = TextAreaField("Delivery Address", validators=[DataRequired()])
    delivery_instructions = TextAreaField("Delivery Instructions (optional)", validators=[Optional()])
    payment_method = RadioField(
        "Payment Method",
        choices=[("cod", "Cash on Delivery"), ("razorpay", "Pay Online (Razorpay)")],
        default="cod",
        validators=[DataRequired()],
    )
    submit = SubmitField("Place Order")


class MenuItemForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional()])
    price = FloatField("Price (₹)", validators=[DataRequired(), NumberRange(min=1)])
    category = SelectField(
        "Category",
        choices=[
            ("Starters", "Starters"),
            ("Main Course", "Main Course"),
            ("Desserts", "Desserts"),
            ("Beverages", "Beverages"),
            ("Sides", "Sides"),
        ],
    )
    is_veg = BooleanField("Vegetarian", default=True)
    preparation_time = IntegerField("Prep Time (minutes)", validators=[NumberRange(min=1, max=180)], default=20)
    is_available = BooleanField("Available", default=True)
    submit = SubmitField("Save Item")


class RestaurantForm(FlaskForm):
    name = StringField("Restaurant Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional()])
    address = TextAreaField("Address", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField("Email", validators=[Optional(), Email()])
    cuisine_type = StringField("Cuisine Type", validators=[DataRequired()])
    opening_time = StringField("Opening Time", validators=[DataRequired()])
    closing_time = StringField("Closing Time", validators=[DataRequired()])
    is_active = BooleanField("Restaurant Open", default=True)
    submit = SubmitField("Save Restaurant")


class ReviewForm(FlaskForm):
    rating = SelectField("Food Rating", choices=[(str(i), f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)])
    delivery_rating = SelectField(
        "Delivery Rating", choices=[(str(i), f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)]
    )
    comment = TextAreaField("Your Review (optional)", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Submit Review")
