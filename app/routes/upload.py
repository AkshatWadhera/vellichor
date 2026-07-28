import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Conversation, PDF
from app import db
from flask_login import current_user
from app.services.document_service import (
    save_pdf,
    allowed_file,
    allowed_mimetype,
)

upload_bp = Blueprint("upload",__name__)

@upload_bp.route("/upload",methods=["POST"])
@login_required
def upload_pdf():

    pdf = request.files.get("pdf")

    print(pdf.mimetype)

    #checking for pdf in request
    if not pdf or pdf.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("main.home"))
    
    #Layer 1 - checking whether filename ends with .pdf
    if not allowed_file(pdf.filename):
        flash("Only PDF files are allowed.", "error")
        return redirect(url_for("main.home"))

    #Layer 2 - Checking for Mimetype
    if not allowed_mimetype(pdf):
        flash("Invalid file type.", "error")
        return redirect(url_for("main.home"))
                
    original_filename, unique_filename, filepath = save_pdf(pdf)
    file_size = os.path.getsize(filepath)

    #Automatically creating a Conversation once the pdf is received/uploaded.
    conversation = Conversation(
        title = original_filename,
        user_id = current_user.id
    )

    db.session.add(conversation)

    #Creating a row in pdf table as well storing the pdf record
    pdf_record = PDF(
        original_filename = original_filename,
        stored_filename = unique_filename,
        file_size = file_size,
        mime_type = pdf.mimetype,
        conversation = conversation
    )

    db.session.add(pdf_record)

    db.session.commit()

    print(conversation.id)

    flash("File received successfully!","success")
    return redirect(url_for("main.home"))
