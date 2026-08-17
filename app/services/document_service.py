import os
import uuid

from werkzeug.utils import secure_filename
from flask import current_app

from supabase import create_client


ALLOWED_MIME_TYPE = "application/pdf"


# =========================================================
# SUPABASE CLIENT
# =========================================================

def get_supabase_client():

    return create_client(
        current_app.config["SUPABASE_URL"],
        current_app.config["SUPABASE_SECRET_KEY"]
    )


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
        return False

    pdf.stream.seek(0)

    file_signature = pdf.stream.read(5)

    pdf.stream.seek(0)

    return file_signature == b"%PDF-"


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

        pdf.save(filepath)

        return (
            original_filename,
            unique_filename,
            filepath
        )


    # -----------------------------------------------------
    # PRODUCTION
    # -----------------------------------------------------

    import tempfile

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    filepath = temp_file.name

    temp_file.close()


    try:

        pdf.save(filepath)


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


        return (
            original_filename,
            unique_filename,
            filepath
        )


    except Exception:

        if os.path.exists(filepath):

            os.remove(filepath)

        raise


def delete_stored_pdf(stored_filename):

    # -------------------------------------------------
    # LOCAL
    # -------------------------------------------------

    if current_app.config["ENVIRONMENT"] == "development":

        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            stored_filename
        )

        if os.path.exists(filepath):
            os.remove(filepath)

        return


    # -------------------------------------------------
    # PRODUCTION
    # -------------------------------------------------

    supabase = get_supabase_client()

    supabase.storage \
        .from_(
            current_app.config["SUPABASE_BUCKET"]
        ) \
        .remove([
            stored_filename
        ])