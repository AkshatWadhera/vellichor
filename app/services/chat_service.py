from app import db
from app.models import Conversation, Message
from app.services import retrieval_service, llm_service

def get_sidebar_conversations(user_id):

    return(
        Conversation.query
        .filter_by(user_id=user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )

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

def save_message(conversation_id, role, content):

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.session.add(message)
    db.session.commit()

    return message

def generate_ai_response(conversation_id, user_message):

    #Save User's Message
    save_message(
        conversation_id,
        "user",
        user_message
    )

    conversation = Conversation.query.get_or_404(conversation_id)
    pdf = conversation.pdf

    retrieved_chunks = retrieval_service.retrieve_chunks(
        user_message,
        pdf.id
    )

    context = "\n\n".join(
        document.page_content for document in retrieved_chunks
    )

    ai_response = llm_service.generate_response(
        user_message,
        context
    )

    assistant_message = save_message(
        conversation_id,
        "assistant",
        ai_response,
    )

    return assistant_message



