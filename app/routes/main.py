import os
from flask import Blueprint, render_template, current_app, jsonify
from flask_login import login_required, current_user

from app.models import Conversation, PDF
from app.services import chat_service, llm_service, embedding_service, retrieval_service

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


@main.route("/test-query/<int:pdf_id>")
def test_query(pdf_id):
    question = "If I only had 5 minutes to study this PDF, what should I learn?"

    results = retrieval_service.retrieve_chunks(question, pdf_id)

    context = "\n\n".join(
        document.page_content for document in results
    )

    print("========== CONTEXT ==========")
    print(context)
    print("=============================")
    
    answer = llm_service.generate_response(question, context)

    return answer