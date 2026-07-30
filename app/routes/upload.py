import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from flask_login import current_user

from app import db
from app.models import Conversation, PDF
from app.services import document_service, embedding_service, retrieval_service


upload_bp = Blueprint("upload",__name__)

@upload_bp.route("/upload",methods=["POST"])
@login_required
def upload_pdf():

    #Receiving the PDF file
    pdf = request.files.get("pdf")

    #VALIDATION 

    #checking for pdf in request
    if not pdf or pdf.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("main.home"))
    
    #Layer 1 - checking whether filename ends with .pdf
    if not document_service.allowed_file(pdf.filename):
        flash("Only PDF files are allowed.", "error")
        return redirect(url_for("main.home"))

    #Layer 2 - Checking for Mimetype
    if not document_service.allowed_mimetype(pdf):
        flash("Invalid file type.", "error")
        return redirect(url_for("main.home"))

    #  SAVING PDF 
                
    original_filename, unique_filename, filepath = document_service.save_pdf(pdf)
    file_size = os.path.getsize(filepath)

    # DATABASE UPDATIONS

    #Automatically creating a Conversation once the pdf is received/uploaded.
    conversation = Conversation(
        title = original_filename,
        user_id = current_user.id
    )

    db.session.add(conversation)
    print("New convo added")

    #Creating a row in pdf table as well storing the pdf record
    pdf_record = PDF(
        original_filename = original_filename,
        stored_filename = unique_filename,
        file_size = file_size,
        mime_type = pdf.mimetype,
        conversation = conversation
    )

    db.session.add(pdf_record)
    print("New PDF record added")

    db.session.commit()


    #  RAG PIPELINE  

    #Extracting text
    text = embedding_service.extract_text(filepath)

    if not text.strip():
        os.remove(filepath)
        print("PDF removed from uploads folder")
        
        db.session.delete(pdf_record)
        print("PDF record removed")
        db.session.delete(conversation)
        print("conversation removed")
        db.session.commit()

        flash(
            "This PDF contains no selectable text. Please upload a text-based PDF.",
            "error"
        )
        return redirect(url_for("main.home"))

        
    

    #Chunking text
    chunks = embedding_service.chunk_text(text)

    #Storing chunks in Chroma and creating Embeddings.
    
    stored_chunks = retrieval_service.store_chunks(
            chunks,
            pdf_record.id,
            pdf_record.original_filename
        )

    print(retrieval_service.vector_store._collection.count())

    flash("File received successfully!","success")
    return redirect(url_for("main.home"))
