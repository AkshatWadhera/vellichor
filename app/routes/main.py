from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint("main",__name__)

@main.route("/")
def landing():
    return render_template("main/landing_page.html")


@main.route("/home")
@login_required
def home():
    return render_template("main/home.html")