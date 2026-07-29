from app import db
from app.models import Conversation, Message

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