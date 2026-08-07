
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
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
        "main/home1.html",
        workspace_state="chat",
        conversations=conversations,
        pinned_conversations=conversations["pinned"],
        recent_conversations=conversations["recent"],
        active_conversation=active_conversation,
        messages=messages,
    )


@chat.route("/<int:conversation_id>/send", methods=["POST"])
@login_required
def send_message(conversation_id):

    content = request.form.get("message", "").strip()

    if not content:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    assistant_message = chat_service.generate_ai_response(
        conversation_id=conversation_id,
        user_message=content,
    )

    return jsonify({

        "user": content,

        "assistant": assistant_message.content

    })


#Route for Deleting Chat
@chat.route("/<int:conversation_id>/delete",methods=["POST"])
def delete_chat(conversation_id):

    chat_service.delete_conversation(conversation_id,current_user.id)

    return redirect(
        url_for(
            "main.home",
        )
    )

#Route for Renaming Chat
@chat.route("/<int:conversation_id>/rename",methods=["POST"])
def rename_chat(conversation_id):

    new_title = request.form.get("title","").strip()

    if new_title:
        chat_service.rename_conversation(conversation_id, current_user.id, new_title)

    return redirect(
        request.referrer or url_for("main.home")
    )


#Route for Pinning Chats
@chat.route("/<int:conversation_id>/pin", methods=["POST"])
@login_required
def toggle_pin(conversation_id):

    chat_service.toggle_pin(
        conversation_id,
        current_user.id
    )

    return redirect(
        request.referrer or url_for("main.home")
    )




    


