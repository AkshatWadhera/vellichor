import time

from flask import current_app

from app import db
from app.models import Conversation, Message
from app.services import retrieval_service, llm_service, document_service


# =========================================================
# READING FUNCTIONS
# =========================================================

def get_sidebar_conversations(user_id):

    try:

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

    except Exception:

        current_app.logger.exception(
            "Failed to load sidebar conversations"
        )

        raise


def get_active_conversation(user_id, conversation_id):

    try:

        return Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first_or_404()

    except Exception:

        current_app.logger.exception(
            "Failed to load active conversation"
        )

        raise


def get_conversation_messages(conversation_id):

    try:

        return (
            Message.query
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    except Exception:

        current_app.logger.exception(
            "Failed to load conversation messages"
        )

        raise


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def save_message(conversation_id, role, content):

    try:

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        db.session.add(message)
        db.session.commit()

        return message

    except Exception:

        current_app.logger.exception(
            "Failed to save conversation message"
        )

        db.session.rollback()

        raise


def build_conversation_history(conversation):

    try:

        messages = conversation.messages[-4:]

        history = "\n".join(
            f"{message.role.capitalize()}: {message.content}"
            for message in messages
        )

        return history

    except Exception:

        current_app.logger.exception(
            "Failed to build conversation history"
        )

        raise


def build_context(chunks):

    try:

        context = "\n\n".join(
            document.page_content
            for document in chunks
        )

        return context

    except Exception:

        current_app.logger.exception(
            "Failed to build retrieved document context"
        )

        raise


# =========================================================
# DELETING CONVERSATION
# =========================================================

def delete_conversation(conversation_id, user_id):

    try:

        total_start = time.perf_counter()

        # -------------------------------------------------
        # FIND CONVERSATION
        # -------------------------------------------------

        lookup_start = time.perf_counter()

        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first_or_404()

        lookup_time = time.perf_counter() - lookup_start

        print(
            f"DELETE TIMING: Conversation lookup completed in {lookup_time:.3f}s",
            flush=True
        )

        pdf = conversation.pdf

        stored_filename = pdf.stored_filename
        pdf_id = pdf.id

        # -------------------------------------------------
        # DELETE STORED PDF
        # -------------------------------------------------

        print(
            "DELETE TIMING: Starting Supabase PDF deletion",
            flush=True
        )

        storage_start = time.perf_counter()

        document_service.delete_stored_pdf(
            stored_filename
        )

        storage_time = time.perf_counter() - storage_start

        print(
            f"DELETE TIMING: Supabase PDF deletion completed in {storage_time:.3f}s",
            flush=True
        )

        # -------------------------------------------------
        # DELETE EMBEDDINGS
        # -------------------------------------------------

        print(
            "DELETE TIMING: Starting PGVector embedding deletion",
            flush=True
        )

        vector_start = time.perf_counter()

        retrieval_service.delete_pdf_embeddings(
            pdf_id
        )

        vector_time = time.perf_counter() - vector_start

        print(
            f"DELETE TIMING: PGVector embedding deletion completed in {vector_time:.3f}s",
            flush=True
        )

        # -------------------------------------------------
        # DELETE DATABASE RECORD
        # -------------------------------------------------

        print(
            "DELETE TIMING: Starting PostgreSQL deletion + commit",
            flush=True
        )

        db_start = time.perf_counter()

        db.session.delete(conversation)
        db.session.commit()

        db_time = time.perf_counter() - db_start

        print(
            f"DELETE TIMING: PostgreSQL deletion + commit completed in {db_time:.3f}s",
            flush=True
        )

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        total_time = time.perf_counter() - total_start

        print(
            f"DELETE TIMING: TOTAL delete_conversation completed in {total_time:.3f}s",
            flush=True
        )

        print(
            "Conversation deleted successfully",
            flush=True
        )

    except Exception:

        current_app.logger.exception(
            "Failed to delete conversation"
        )

        db.session.rollback()

        raise


# =========================================================
# RENAMING CONVERSATION
# =========================================================

def rename_conversation(
    conversation_id,
    user_id,
    new_title
):

    try:

        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first_or_404()


        conversation.title = new_title.strip()

        db.session.commit()


        current_app.logger.info(
            "Conversation renamed successfully"
        )

    except Exception:

        current_app.logger.exception(
            "Failed to rename conversation"
        )

        db.session.rollback()

        raise


# =========================================================
# PIN CHATS
# =========================================================

def toggle_pin(conversation_id, user_id):

    try:

        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id,
        ).first_or_404()


        conversation.is_pinned = not conversation.is_pinned

        db.session.commit()


        current_app.logger.info(
            "Conversation pin state updated"
        )

    except Exception:

        current_app.logger.exception(
            "Failed to update conversation pin state"
        )

        db.session.rollback()

        raise


# =========================================================
# RESPONSIBLE FOR GENERATING AI RESPONSE
# =========================================================

def generate_ai_response(
    conversation_id,
    user_message
):

    try:

        # -------------------------------------------------
        # SAVE USER MESSAGE
        # -------------------------------------------------

        current_app.logger.info(
            "Saving user message"
        )

        save_message(
            conversation_id,
            "user",
            user_message
        )


        # -------------------------------------------------
        # ACCESS CONVERSATION + PDF
        # -------------------------------------------------

        conversation = Conversation.query.get_or_404(
            conversation_id
        )

        pdf = conversation.pdf


        # -------------------------------------------------
        # BUILD CONVERSATION HISTORY
        # -------------------------------------------------

        history = build_conversation_history(
            conversation
        )


        # -------------------------------------------------
        # RETRIEVE RELEVANT PDF CHUNKS
        # -------------------------------------------------

        current_app.logger.info(
            "Retrieving relevant PDF chunks"
        )

        chunks = retrieval_service.retrieve_chunks(
            user_message,
            pdf.id
        )


        current_app.logger.info(
            "PDF chunk retrieval completed: %s results",
            len(chunks)
        )


        # -------------------------------------------------
        # BUILD CONTEXT
        # -------------------------------------------------

        context = build_context(
            chunks
        )


        # -------------------------------------------------
        # GENERATE AI RESPONSE
        # -------------------------------------------------

        current_app.logger.info(
            "Generating AI response"
        )

        ai_response = llm_service.generate_response(
            user_message,
            context,
            history
        )


        current_app.logger.info(
            "AI response generated successfully"
        )


        # -------------------------------------------------
        # SAVE ASSISTANT MESSAGE
        # -------------------------------------------------

        assistant_message = save_message(
            conversation_id,
            "assistant",
            ai_response
        )


        current_app.logger.info(
            "Assistant message saved successfully"
        )


        return assistant_message


    except Exception:

        current_app.logger.exception(
            "Failed to generate AI response"
        )

        raise