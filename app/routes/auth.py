from flask import Blueprint, render_template, request

auth = Blueprint("auth", __name__)

@auth.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")

        return f"Email: {email}, Password: {password}"
    
    return render_template("auth/register.html")