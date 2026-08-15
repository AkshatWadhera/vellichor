import re
from flask import Blueprint, request, flash, redirect, url_for, current_app, jsonify

from app import db
from app.models.user import User

from flask_login import (
    login_user,
    logout_user,
    login_required
)


auth = Blueprint("auth", __name__)


# =========================================================
# REGISTER
# =========================================================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")


        # -------------------------------------------------
        # Basic server-side validation
        # -------------------------------------------------

        if not name:
            return jsonify({
                "success":False,
                "field":"name",
                "message":"Please enter your name."
            }),400

        if not email:
            return jsonify({
                "success": False,
                "field": "email",
                "message": "Please enter your email address."
            }), 400


        if not re.match(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email
        ):
            return jsonify({
                "success": False,
                "field": "email",
                "message": "Please enter a valid email address."
            }), 400
    

        if not password:
            return jsonify({
                "success": False,
                "field": "password",
                "message": "Please enter a password."
            }), 400


        # -------------------------------------------------
        # Existing account
        # -------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            return jsonify({
                "success": False,
                "field": "email",
                "message": "An account with this email already exists."
            }), 409


        # -------------------------------------------------
        # Create user
        # -------------------------------------------------

        try:

            user = User(
                name=name,
                email=email
            )

            user.set_password(password)

            db.session.add(user)
            db.session.commit()


        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "Error while registering user."
            )

            return jsonify({
                "success": False,
                "field": "general",
                "message": "We couldn't create your account right now. Please try again."
            }), 500


        # -------------------------------------------------
        # Registration successful
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "redirect": url_for(
                "main.landing",
                state="login"
            )
        })


    return redirect(
        url_for(
            "main.landing",
            state="register"
        )
    )


# =========================================================
# LOGIN
# =========================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # -------------------------------------------------
        # Basic server-side validation
        # -------------------------------------------------

        if not email:
            return jsonify({
                "success": False,
                "field": "email",
                "message": "Please enter your email address."
            }), 400


        if not password:
            return jsonify({
                "success": False,
                "field": "password",
                "message": "Please enter your password."
            }), 400


        # -------------------------------------------------
        # Find user
        # -------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()


        # -------------------------------------------------
        # Invalid credentials
        # -------------------------------------------------

        if existing_user is None:

            return jsonify({
                "success": False,
                "field": "general",
                "message": "Invalid email or password."
            }), 401


        if not existing_user.check_password(password):

            return jsonify({
                "success": False,
                "field": "general",
                "message": "Invalid email or password."
            }), 401


        # -------------------------------------------------
        # Login successful
        # -------------------------------------------------

        login_user(existing_user)

        return jsonify({
            "success": True,
            "redirect": url_for("main.home")
        })


    return redirect(
        url_for(
            "main.landing",
            state="login"
        )
    )


# =========================================================
# LOGOUT
# =========================================================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("main.landing")
    )