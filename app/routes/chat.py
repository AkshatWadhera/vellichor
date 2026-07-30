
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user


from app.models import Conversation
from app.services import chat_service

chat = Blueprint("chat", __name__)

@chat.route("/chat/<int:conversation_id>")
@login_required
def open_chat(conversation_id):

    conversations = chat_service.get_sidebar_conversations(current_user.id)

    active_conversation = chat_service.get_active_conversation(current_user.id, conversation_id)

    messages = chat_service.get_conversation_messages(conversation_id)

    return render_template(
        "main/home.html",
        workspace_state="chat",
        conversations=conversations,
        active_conversation=active_conversation,
        messages=messages,
    )


@chat.route("/<int:conversation_id>/send", methods=["POST"])
@login_required
def send_message(conversation_id):

    content = request.form.get("message", "").strip()

    if content:
        chat_service.generate_ai_response(
            conversation_id=conversation_id,
            user_message=content,
        )

    return redirect(
        url_for(
            "chat.open_chat",
            conversation_id=conversation_id
        )
    )

