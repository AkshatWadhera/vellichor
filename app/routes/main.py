from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import Conversation
from app.services import chat_service

main = Blueprint("main",__name__)

@main.route("/")
def landing():
    return render_template("main/landing_page.html")


@main.route("/home")
@login_required
def home():

    #For Sidebar Conversations
    conversations = chat_service.get_sidebar_conversations(current_user.id)

    return render_template(
        "main/home.html",
        workspace_state = "upload",
        conversations = conversations,
        active_conversation = None 
    )