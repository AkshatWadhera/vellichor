import os
import time

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from app import db
from app.models import Conversation, PDF
from app.services import document_service, embedding_service, retrieval_service


upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload_pdf():

    upload_start = time.perf_counter()

    current_app.logger.info(
        "========== VELLICHOR PDF INGESTION START =========="
    )

    # ========================================
    # RECEIVING PDF
    # ========================================

    pdf = request.files.get("pdf")

    # ========================================
    # VALIDATION
    # ========================================

    validation_start = time.perf_counter()

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

    validation_time = time.perf_counter() - validation_start

    current_app.logger.info(
        "[01] Validation completed in %.3fs",
        validation_time
    )

    original_filename = None
    unique_filename = None
    filepath = None
    file_size = 0

    # ========================================
    # SAVING PDF
    # ========================================

    save_start = time.perf_counter()

    try:

        original_filename, unique_filename, filepath = \
            document_service.save_pdf(pdf)

        file_size = os.path.getsize(filepath)

        save_time = time.perf_counter() - save_start

        current_app.logger.info(
            "[02] PDF storage completed in %.3fs | File: %s | Size: %.2f KB",
            save_time,
            original_filename,
            file_size / 1024
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

        db_start = time.perf_counter()

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

        db_time = time.perf_counter() - db_start

        current_app.logger.info(
            "[03] Database records created in %.3fs | PDF ID: %s | Conversation ID: %s",
            db_time,
            pdf_record.id,
            conversation.id
        )

        # ========================================
        # TEXT EXTRACTION
        # ========================================

        extraction_start = time.perf_counter()

        current_app.logger.info(
            "[04] Starting PDF text extraction"
        )

        text = embedding_service.extract_text(filepath)

        extraction_time = time.perf_counter() - extraction_start

        current_app.logger.info(
            "[04] PDF text extraction completed in %.3fs | Characters: %s",
            extraction_time,
            len(text)
        )

        # Check for PDFs with no selectable text

        if not text.strip():
            raise ValueError("NO_TEXT")

        # ========================================
        # CHUNKING
        # ========================================

        chunking_start = time.perf_counter()

        current_app.logger.info(
            "[05] Starting PDF chunking"
        )

        chunks = embedding_service.chunk_text(text)

        chunking_time = time.perf_counter() - chunking_start

        current_app.logger.info(
            "[05] PDF chunking completed in %.3fs | Chunks: %s",
            chunking_time,
            len(chunks)
        )

        # ========================================
        # EMBEDDINGS + VECTOR STORAGE
        # ========================================

        vector_start = time.perf_counter()

        current_app.logger.info(
            "[06] Starting embedding generation + vector storage"
        )

        retrieval_service.store_chunks(
            chunks,
            pdf_record.id,
            pdf_record.original_filename
        )

        vector_time = time.perf_counter() - vector_start

        embeddings_stored = True

        current_app.logger.info(
            "[06] Embedding + vector storage completed in %.3fs",
            vector_time
        )

        # ========================================
        # EVERYTHING SUCCESSFUL
        # ========================================

        commit_start = time.perf_counter()

        db.session.commit()

        commit_time = time.perf_counter() - commit_start

        current_app.logger.info(
            "[07] Database transaction committed in %.3fs",
            commit_time
        )

        # ========================================
        # CLEANUP
        # ========================================

        cleanup_start = time.perf_counter()

        if (
            current_app.config["ENVIRONMENT"] == "production"
            and os.path.exists(filepath)
        ):

            os.remove(filepath)

            current_app.logger.info(
                "Temporary production PDF removed: %s",
                original_filename
            )

        cleanup_time = time.perf_counter() - cleanup_start

        # ========================================
        # FINAL TIMING
        # ========================================

        total_time = time.perf_counter() - upload_start

        current_app.logger.info(
            "[08] Cleanup completed in %.3fs",
            cleanup_time
        )

        current_app.logger.info(
            "========== VELLICHOR PDF INGESTION COMPLETE =========="
        )

        current_app.logger.info(
            "TOTAL PDF INGESTION TIME: %.3fs | File: %s | Size: %.2f KB | Chunks: %s",
            total_time,
            original_filename,
            file_size / 1024,
            len(chunks)
        )

        return jsonify({
            "success": True,
            "conversation_id": conversation.id
        })

    except ValueError as error:

        error_code = str(error)

        current_app.logger.info(
            "Expected PDF processing error: %s",
            error_code
        )

        if embeddings_stored and pdf_record:

            try:

                retrieval_service.delete_pdf_embeddings(
                    pdf_record.id
                )

            except Exception:

                current_app.logger.exception(
                    "Failed to remove embeddings during PDF cleanup"
                )

        db.session.rollback()

        if filepath and os.path.exists(filepath):

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

        current_app.logger.exception(
            "PDF processing failed"
        )

        if embeddings_stored and pdf_record:

            try:

                retrieval_service.delete_pdf_embeddings(
                    pdf_record.id
                )

            except Exception:

                current_app.logger.exception(
                    "Failed to remove embeddings during PDF cleanup"
                )

        db.session.rollback()

        if filepath and os.path.exists(filepath):

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