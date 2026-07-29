import os
from flask import Blueprint, render_template, current_app, jsonify
from flask_login import login_required, current_user

from app.models import Conversation, PDF
from app.services import chat_service, llm_service, embedding_service, retrieval_service

main = Blueprint("main",__name__)


@main.route("/")
def landing():
    return render_template("main/landing_page.html")

@main.route("/test-groq")
def groq_test():
    return llm_service.test_groq()

@main.route("/test-extract/<int:pdf_id>")
def test_extract(pdf_id):
    pdf = PDF.query.get_or_404(pdf_id)

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        pdf.stored_filename
    )

    text = embedding_service.extract_text(filepath)

    return f"<pre>{text[:5000]}</pre>"

@main.route("/test-chunks/<int:pdf_id>")
def test_chunks(pdf_id):
    pdf = PDF.query.get_or_404(pdf_id)

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        pdf.stored_filename
    )

    text = embedding_service.extract_text(filepath)

    chunks = embedding_service.chunk_text(text)

    output = f"Total Chunks: {len(chunks)}\n\n"

    for i, chunk in enumerate(chunks[:3], start=1):
        output += f"----- Chunk {i} -----\n"
        output += f"Length: {len(chunk)} characters\n\n"
        output += chunk[:500]
        output += "\n\n"

    return f"<pre>{output}</pre>"


@main.route("/test-embeddings/<int:pdf_id>")
def test_embeddings(pdf_id):
    pdf = PDF.query.get_or_404(pdf_id)

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        pdf.stored_filename
    )

    text = embedding_service.extract_text(filepath)

    chunks = embedding_service.chunk_text(text)

    embeddings = embedding_service.generate_embeddings(chunks)

    return {
        "total_chunks": len(chunks),
        "total_embeddings": len(embeddings),
        "embedding_dimension": len(embeddings[0]),
        "first_10_values": embeddings[0][:10]
    }

@main.route("/test-chroma/<int:pdf_id>")
def test_chroma(pdf_id):

    pdf = PDF.query.get_or_404(pdf_id)

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        pdf.stored_filename
    )

    text = embedding_service.extract_text(filepath)

    chunks = embedding_service.chunk_text(text)

    stored_chunks = retrieval_service.store_chunks(
        chunks,
        pdf.id,
        pdf.original_filename
    )

    return jsonify({
        "message": "Stored successfully",
        "chunks_stored": stored_chunks
    })

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