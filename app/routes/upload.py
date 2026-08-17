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

    try:

        original_filename, unique_filename, filepath = \
            document_service.save_pdf(pdf)

        file_size = os.path.getsize(filepath)

        current_app.logger.info(
            "PDF saved successfully: %s",
            original_filename
        )

    except Exception:

        current_app.logger.exception(
            "PDF storage failed"
        )

        return jsonify({
            "success": False,
            "error_code": "PROCESSING_FAILED"
        }), 500


    conversation = None
    pdf_record = None
    embeddings_stored = False

    current_app.logger.info(
        "Beginning PDF processing: %s",
        original_filename
    )


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

        current_app.logger.info(
            "Database records created for PDF: %s",
            original_filename
        )


        # ========================================
        # RAG PIPELINE
        # ========================================

        # Extract text

        current_app.logger.info(
            "Extracting text from PDF: %s",
            original_filename
        )

        text = embedding_service.extract_text(filepath)

        current_app.logger.info(
            "PDF text extraction completed: %s",
            original_filename
        )


        # Check for PDFs with no selectable text

        if not text.strip():

            raise ValueError("NO_TEXT")


        # Chunk text

        current_app.logger.info(
            "Chunking PDF text: %s",
            original_filename
        )

        chunks = embedding_service.chunk_text(text)

        current_app.logger.info(
            "PDF chunking completed: %s chunks",
            len(chunks)
        )


        # Store chunks + embeddings

        current_app.logger.info(
            "Storing embeddings for PDF: %s",
            original_filename
        )

        retrieval_service.store_chunks(
            chunks,
            pdf_record.id,
            pdf_record.original_filename
        )

        embeddings_stored = True

        current_app.logger.info(
            "Embeddings stored successfully for PDF: %s",
            original_filename
        )


        # ========================================
        # EVERYTHING SUCCESSFUL
        # ========================================

        db.session.commit()

        current_app.logger.info(
            "PDF database transaction committed: %s",
            original_filename
        )


        # Remove temporary production file

        if (
            current_app.config["ENVIRONMENT"] == "production"
            and os.path.exists(filepath)
        ):

            os.remove(filepath)

            current_app.logger.info(
                "Temporary production PDF removed: %s",
                original_filename
            )


        return jsonify({
            "success": True,
            "conversation_id": conversation.id
        })


    except ValueError as error:

        # ========================================
        # EXPECTED PDF ERRORS
        # ========================================

        error_code = str(error)

        current_app.logger.info(
            "Expected PDF processing error: %s",
            error_code
        )


        # Remove embeddings if they were created

        if embeddings_stored and pdf_record:

            try:

                retrieval_service.delete_pdf_embeddings(
                    pdf_record.id
                )

            except Exception:

                current_app.logger.exception(
                    "Failed to remove embeddings during PDF cleanup"
                )


        # Roll back database transaction

        db.session.rollback()


        # Remove physical PDF

        if os.path.exists(filepath):

            try:

                os.remove(filepath)

            except PermissionError:

                current_app.logger.exception(
                    "Unable to remove PDF during cleanup"
                )


        return jsonify({
            "success": False,
            "error_code": error_code
        }), 400


    except Exception:

        # ========================================
        # UNEXPECTED PROCESSING ERROR
        # ========================================

        current_app.logger.exception(
            "PDF processing failed"
        )


        # Remove embeddings if they were created

        if embeddings_stored and pdf_record:

            try:

                retrieval_service.delete_pdf_embeddings(
                    pdf_record.id
                )

            except Exception:

                current_app.logger.exception(
                    "Failed to remove embeddings during PDF cleanup"
                )


        # Roll back database transaction

        db.session.rollback()


        # Remove physical PDF

        if os.path.exists(filepath):

            try:

                os.remove(filepath)

            except PermissionError:

                current_app.logger.exception(
                    "Unable to remove PDF during cleanup"
                )


        return jsonify({
            "success": False,
            "error_code": "PROCESSING_FAILED"
        }), 500