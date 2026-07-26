from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from app.models.user import User
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required

auth = Blueprint("auth", __name__)

@auth.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists"

        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successfull! Please log in.","success")
        return redirect(url_for("auth.register"))
    
    return render_template("auth/register.html")

@auth.route("/login",methods=["GET","POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user is None:
            flash("Invalid email or password.","danger")
            return redirect(url_for("auth.login"))

        if not existing_user.check_password(password):
            flash("Invalid email or password.","danger")
            return redirect(url_for("auth.login"))

        login_user(existing_user)

        
        return redirect(url_for("main.home"))


    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have been logged out. ","success")
    return redirect(url_for("main.landing"))