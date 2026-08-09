import os
from flask import Blueprint, render_template, current_app, jsonify, request
from flask_login import login_required, current_user

from app.models import Conversation, PDF
from app.services import chat_service, llm_service, embedding_service, retrieval_service

main = Blueprint("main",__name__)


@main.route("/")
def landing():

    state = request.args.get("state", "intro")

    return render_template(
        "main/landing_page.html",
        landing_state=state
    )



@main.route("/home")
@login_required
def home():

    #For Sidebar Conversations
    conversations = chat_service.get_sidebar_conversations(current_user.id)

    return render_template(
        "main/home1.html",
        workspace_state = "upload",
        conversations = conversations,
        pinned_conversations=conversations["pinned"],
        recent_conversations=conversations["recent"],
        active_conversation = None 
    )


