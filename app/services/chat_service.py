import os
from flask import current_app

from app import db
from app.models import Conversation, Message
from app.services import retrieval_service, llm_service, document_service

# Reading Functions

def get_sidebar_conversations(user_id):

    conversations = (
        Conversation.query
        .filter_by(user_id=user_id)
        .order_by(
            Conversation.is_pinned.desc(),
            Conversation.created_at.desc()
        )
        .all()
    )

    return {
        "pinned": [
            c for c in conversations
            if c.is_pinned
        ],
        "recent": [
            c for c in conversations
            if not c.is_pinned
        ]
    }



def get_active_conversation(user_id, conversation_id):

    return Conversation.query.filter_by(
        id=conversation_id,
        user_id=user_id
    ).first_or_404()


def get_conversation_messages(conversation_id):

    return(
        Message.query
        .filter_by(conversation_id=conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

#Helper Functions

def save_message(conversation_id, role, content):

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.session.add(message)
    db.session.commit()

    return message

def build_conversation_history(conversation):
    messages = conversation.messages[-10:]

    history = "\n".join(
        f"{message.role.capitalize()}: {message.content}"
        for message in messages
    )

    return history

def build_context(chunks):
    context = "\n\n".join(
        document.page_content for document in chunks
    )

    return context


#Deleting Conversation
def delete_conversation(conversation_id, user_id):
    conversation = Conversation.query.filter_by(
        id = conversation_id,
        user_id = user_id
    ).first_or_404()
    
   
    pdf = conversation.pdf
    

    stored_filename = pdf.stored_filename
    pdf_id = pdf.id

    document_service.delete_stored_pdf(stored_filename)

    retrieval_service.delete_pdf_embeddings(pdf_id)

    db.session.delete(conversation)
    db.session.commit()


#Renaming Conversation
def rename_conversation(conversation_id, user_id, new_title):
    conversation = Conversation.query.filter_by(
        id = conversation_id,
        user_id = user_id
    ).first_or_404()

    conversation.title = new_title.strip()

    db.session.commit()

# Pin Chats
def toggle_pin(conversation_id, user_id):
    conversation = Conversation.query.filter_by(
        id = conversation_id,
        user_id = user_id,
    ).first_or_404()

    conversation.is_pinned = not conversation.is_pinned

    db.session.commit()


#Responsible for generating AI Response
def generate_ai_response(conversation_id, user_message):

    #Save User's Message
    save_message(
        conversation_id,
        "user",
        user_message
    )

    #Accessing the current conversation and the PDF uploaded
    conversation = Conversation.query.get_or_404(conversation_id)
    pdf = conversation.pdf

    #Building Conversation History
    history = build_conversation_history(conversation)

    #Responsbile for retrieving generated chunks
    chunks = retrieval_service.retrieve_chunks(
        user_message,
        pdf.id
    )

    #Generating Context (PDF chunking)
    context = build_context(chunks)

    #AI Response Generated (Sending User Message + PDF Context Chunks)
    
    ai_response = llm_service.generate_response(
        user_message,
        context,
        history
    )

    #AI Message saved in the Database
    assistant_message = save_message(
        conversation_id,
        "assistant",
        ai_response,
    )

    return assistant_message



