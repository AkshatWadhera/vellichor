import os

from flask import Blueprint, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Conversation, PDF
from app.services import document_service, embedding_service, retrieval_service


upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload_pdf():

    # Receiving the PDF file
    pdf = request.files.get("pdf")


    # ========================================
    # VALIDATION
    # ========================================

    # Checking for PDF in request
    if not pdf or pdf.filename == "":

        return jsonify({
            "success": False,
            "error_code": "NO_FILE"
        }), 400


    # Layer 1 - checking whether filename ends with .pdf
    if not document_service.allowed_file(pdf.filename):

        return jsonify({
            "success": False,
            "error_code": "INVALID_EXTENSION"
        }), 400


    # Layer 2 - checking MIME type
    if not document_service.allowed_mimetype(pdf):

        return jsonify({
            "success": False,
            "error_code": "INVALID_MIME"
        }), 400


    # ========================================
    # SAVING PDF
    # ========================================

    original_filename, unique_filename, filepath = \
        document_service.save_pdf(pdf)

    file_size = os.path.getsize(filepath)


    # ========================================
    # DATABASE UPDATES
    # ========================================

    # Automatically creating a Conversation
    # once the PDF is received/uploaded.
    conversation = Conversation(
        title=original_filename,
        user_id=current_user.id
    )

    db.session.add(conversation)

    print("New convo added")


    # Creating a row in PDF table
    pdf_record = PDF(
        original_filename=original_filename,
        stored_filename=unique_filename,
        file_size=file_size,
        mime_type=pdf.mimetype,
        conversation=conversation
    )

    db.session.add(pdf_record)

    print("New PDF record added")

    db.session.commit()


    # ========================================
    # RAG PIPELINE
    # ========================================

    # Extracting text
    text = embedding_service.extract_text(filepath)

    if not text.strip():

        os.remove(filepath)

        print("PDF removed from uploads folder")

        db.session.delete(pdf_record)

        print("PDF record removed")

        db.session.delete(conversation)

        print("conversation removed")

        db.session.commit()

        return jsonify({
            "success": False,
            "error_code": "NO_TEXT"
        }), 400


    # Chunking text
    chunks = embedding_service.chunk_text(text)


    # Storing chunks in Chroma
    # and creating embeddings.
    stored_chunks = retrieval_service.store_chunks(
        chunks,
        pdf_record.id,
        pdf_record.original_filename
    )

    print(retrieval_service.vector_store._collection.count())


    # ========================================
    # SUCCESS
    # ========================================

    return jsonify({
        "success": True,
        "conversation_id": conversation.id
    })