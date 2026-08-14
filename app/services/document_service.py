ALLOWED_MIME_TYPE = "application/pdf"
import os 
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

#checking if the filename ends with .pdf only
def allowed_file(filename):
    return(
        "." in filename and filename.rsplit(".",1)[1].lower() == "pdf"
    )

#Checking for Mimetype
def allowed_mimetype(pdf):

    if pdf.mimetype != ALLOWED_MIME_TYPE:
        return False

    pdf.stream.seek(0)

    file_signature = pdf.stream.read(5)

    pdf.stream.seek(0)

    return file_signature == b"%PDF-"

#Saving PDF in uploads folder
def save_pdf(pdf):
    original_filename = secure_filename(pdf.filename)

    unique_filename = f"{uuid.uuid4()}.pdf"

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    pdf.save(filepath)

    return original_filename, unique_filename, filepath