import os

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from app import db
from app.models import Conversation, PDF
from app.services import document_service, embedding_service, retrieval_service


upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload_pdf():

    # ========================================
    # RECEIVING PDF
    # ========================================

    pdf = request.files.get("pdf")


    # ========================================
    # VALIDATION
    # ========================================

    if not pdf or pdf.filename == "":

        return jsonify({
            "success": False,
            "error_code": "NO_FILE"
        }), 400


    if not document_service.allowed_file(pdf.filename):

        return jsonify({
            "success": False,
            "error_code": "INVALID_EXTENSION"
        }), 400


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


    conversation = None
    pdf_record = None
    embeddings_stored = False

    print("Saved temporary PDF:", filepath)


    try:

        # ========================================
        # DATABASE RECORDS
        # ========================================

        conversation = Conversation(
            title=original_filename,
            user_id=current_user.id
        )

        db.session.add(conversation)


        pdf_record = PDF(
            original_filename=original_filename,
            stored_filename=unique_filename,
            file_size=file_size,
            mime_type=pdf.mimetype,
            conversation=conversation
        )

        db.session.add(pdf_record)


        # Flush gives us database-generated IDs
        # without permanently committing the transaction.

        db.session.flush()


        # ========================================
        # RAG PIPELINE
        # ========================================

        # Extract text

        text = embedding_service.extract_text(filepath)


        # Check for PDFs with no selectable text

        if not text.strip():

            raise ValueError("NO_TEXT")


        # Chunk text

        chunks = embedding_service.chunk_text(text)


        # Store chunks + embeddings in Chroma

        retrieval_service.store_chunks(
            chunks,
            pdf_record.id,
            pdf_record.original_filename
        )

        embeddings_stored = True


        # ========================================
        # EVERYTHING SUCCESSFUL
        # ========================================

        db.session.commit()

        if (
            current_app.config["ENVIRONMENT"] == "production"
            and os.path.exists(filepath)
        ):

            os.remove(filepath)

        return jsonify({
            "success": True,
            "conversation_id": conversation.id
        })


    except ValueError as error:

        # ========================================
        # EXPECTED PDF ERRORS
        # ========================================

        error_code = str(error)


        # Remove Chroma embeddings if they were created

        if embeddings_stored and pdf_record:

            try:

                retrieval_service.delete_pdf_embeddings(
                    pdf_record.id
                )

            except Exception:

                pass


        # Roll back database transaction

        db.session.rollback()


        # Remove physical PDF

        if os.path.exists(filepath):

            try:

                os.remove(filepath)

            except PermissionError:

                pass


        return jsonify({
            "success": False,
            "error_code": error_code
        }), 400


    except Exception:

        # ========================================
        # UNEXPECTED PROCESSING ERROR
        # ========================================

        if embeddings_stored and pdf_record:

            try:

                retrieval_service.delete_pdf_embeddings(
                    pdf_record.id
                )

            except Exception:

                pass


        db.session.rollback()


        try:

            document_service.delete_stored_pdf(
                unique_filename
            )

        except Exception:

            pass


        if os.path.exists(filepath):

            try:

                os.remove(filepath)

            except PermissionError:

                pass


        return jsonify({
            "success": False,
            "error_code": "PROCESSING_FAILED"
        }), 500