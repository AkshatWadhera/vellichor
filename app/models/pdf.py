from app import db
from datetime import datetime

class PDF(db.Model):
    __tablename__ = "pdfs"

    id = db.Column(db.Integer, primary_key=True)

    original_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    stored_filename = db.Column(
            db.String(255),
            nullable=False,
            unique=True
    )

    file_size = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    mime_type = db.Column(
        db.String(100),
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False,
        unique=True
    )