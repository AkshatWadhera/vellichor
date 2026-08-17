import os
import uuid
import tempfile

from werkzeug.utils import secure_filename
from flask import current_app

from supabase import create_client


ALLOWED_MIME_TYPE = "application/pdf"


# =========================================================
# SUPABASE CLIENT
# =========================================================

def get_supabase_client():

    try:

        return create_client(
            current_app.config["SUPABASE_URL"],
            current_app.config["SUPABASE_SECRET_KEY"]
        )

    except Exception:

        current_app.logger.exception(
            "Failed to create Supabase client"
        )

        raise


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() == "pdf"
    )


def allowed_mimetype(pdf):

    if pdf.mimetype != ALLOWED_MIME_TYPE:

        current_app.logger.info(
            "PDF rejected due to invalid MIME type: %s",
            pdf.mimetype
        )

        return False


    pdf.stream.seek(0)

    file_signature = pdf.stream.read(5)

    pdf.stream.seek(0)

    is_valid = file_signature == b"%PDF-"


    if not is_valid:

        current_app.logger.info(
            "PDF rejected due to invalid file signature"
        )


    return is_valid


# =========================================================
# SAVE PDF
# =========================================================

def save_pdf(pdf):

    original_filename = secure_filename(
        pdf.filename
    )

    unique_filename = f"{uuid.uuid4()}.pdf"


    # -----------------------------------------------------
    # LOCAL DEVELOPMENT
    # -----------------------------------------------------

    if current_app.config["ENVIRONMENT"] == "development":

        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            unique_filename
        )


        try:

            pdf.save(filepath)

            current_app.logger.info(
                "PDF saved to local filesystem: %s",
                original_filename
            )

        except Exception:

            current_app.logger.exception(
                "Failed to save PDF to local filesystem"
            )

            raise


        return (
            original_filename,
            unique_filename,
            filepath
        )


    # -----------------------------------------------------
    # PRODUCTION
    # -----------------------------------------------------

    filepath = None


    try:

        # Temporary local file used only during processing.

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        filepath = temp_file.name

        temp_file.close()


        pdf.save(filepath)

        current_app.logger.info(
            "Production PDF saved to temporary file"
        )


        # -------------------------------------------------
        # SUPABASE STORAGE
        # -------------------------------------------------

        current_app.logger.info(
            "Uploading PDF to Supabase Storage"
        )


        supabase = get_supabase_client()


        with open(filepath, "rb") as file:

            supabase.storage \
                .from_(
                    current_app.config["SUPABASE_BUCKET"]
                ) \
                .upload(
                    path=unique_filename,
                    file=file,
                    file_options={
                        "content-type": ALLOWED_MIME_TYPE
                    }
                )


        current_app.logger.info(
            "PDF uploaded successfully to Supabase Storage"
        )


        return (
            original_filename,
            unique_filename,
            filepath
        )


    except Exception:

        current_app.logger.exception(
            "Failed during production PDF storage"
        )


        # Remove temporary file if it exists.

        if filepath and os.path.exists(filepath):

            try:

                os.remove(filepath)

            except Exception:

                current_app.logger.exception(
                    "Failed to remove temporary PDF after storage error"
                )


        raise


# =========================================================
# DELETE STORED PDF
# =========================================================

def delete_stored_pdf(stored_filename):

    # -----------------------------------------------------
    # LOCAL DEVELOPMENT
    # -----------------------------------------------------

    if current_app.config["ENVIRONMENT"] == "development":

        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            stored_filename
        )


        if os.path.exists(filepath):

            try:

                os.remove(filepath)

                current_app.logger.info(
                    "Local PDF deleted successfully"
                )

            except Exception:

                current_app.logger.exception(
                    "Failed to delete local PDF"
                )

                raise

        else:

            current_app.logger.info(
                "Local PDF was already absent during deletion"
            )


        return


    # -----------------------------------------------------
    # PRODUCTION
    # -----------------------------------------------------

    try:

        current_app.logger.info(
            "Deleting PDF from Supabase Storage"
        )


        supabase = get_supabase_client()


        supabase.storage \
            .from_(
                current_app.config["SUPABASE_BUCKET"]
            ) \
            .remove([
                stored_filename
            ])


        current_app.logger.info(
            "PDF deleted successfully from Supabase Storage"
        )


    except Exception:

        current_app.logger.exception(
            "Failed to delete PDF from Supabase Storage"
        )

        raise